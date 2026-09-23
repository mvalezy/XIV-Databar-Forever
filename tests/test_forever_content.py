"""Real Lua module regressions with narrow client API stubs."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]

class ContentTests(unittest.TestCase):
    def runtime(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('''
            function noop() end
            addon = {compat = {isForever = true, isMainline = true, isRetail = false},
                L = {}, constants = {mediaPath = "", popupPadding = 3},
                db = {char = {portItem = {}}, profile = {modules = {microMenu = {
                    guild = true, hideSocialText = false, osSocialText = 0}},
                    general = {barPosition = "BOTTOM"}}}, modules = {}}
            function addon:NewModule(name)
                local m = {RegisterEvent = noop}
                self.modules[name] = m
                return m
            end
            C_Item = {GetItemInfo = noop, IsUsableItem = function() return true end}
            C_Container = {GetItemCooldown = noop}
            C_Spell = {GetSpellCooldown = noop, GetSpellInfo = noop}
            C_AddOns = {IsAddOnLoaded = function() return false end}
            C_Housing = {GetPlayerOwnedHouses = function() error("Retail housing requested") end}
            Enum = {}
            widget = {EnableMouse = noop, RegisterForClicks = noop,
                SetAttribute = noop, SetScript = noop, Hide = noop, Show = noop,
                SetPoint = noop, SetText = noop}
            function InCombatLockdown() return false end
            function IsInGuild() return true end
            function GetGuildRosterMOTD() return "MOTD" end
            function GetNumGuildMembers() return 5, 2 end
            function GetTime() return 100 end
            requests = 0
            C_GuildInfo = {GuildRoster = function() requests = requests + 1 end}
        ''')
        return lua

    def load(self, lua, file):
        lua.execute((ROOT / file).read_text(), 'XIV_Databar_Continued', lua.globals()['addon'])

    def test_travel_uses_modern_item_usability(self):
        lua = self.runtime()
        lua.execute('function PlayerHasToy() return false end; function IsPlayerSpell() return false end')
        self.load(lua, 'Core/modules/travel.lua')
        lua.execute('assert(addon.modules.TravelModule:IsUsable(6948) == true)')

    def test_forever_initialization_does_not_query_dalaran_item(self):
        lua = self.runtime()
        lua.execute('''
            addon.db.char = {}
            C_Item.GetItemInfo = function(id) error("unexpected item query: " .. id) end
        ''')
        self.load(lua, 'Core/modules/travel.lua')
        lua.execute('addon.modules.TravelModule:OnInitialize()')

    def test_forever_never_requests_housing_or_enables_mythic_travel(self):
        lua = self.runtime()
        self.load(lua, 'Core/modules/travel.lua')
        lua.execute('''
            local m = addon.modules.TravelModule
            m:OnInitialize()
            m.hearthButton, m.portButton, m.portPopup = widget, widget, widget
            m:RegisterFrameEvents()
            local _, defaults = m:GetDefaultOptions()
            assert(not defaults.enableMythicPortals)
            assert(#m.hearthstones < 10, "Retail hearthstone catalog loaded")
        ''')

    def test_forever_menu_does_not_create_housing_button_from_retail_profile(self):
        lua = self.runtime()
        lua.execute('''
            addon.db.profile.modules.microMenu = {house = true}
            addon.GetFrame = function() return widget end
            function CreateFrame() error("unexpected housing button") end
        ''')
        self.load(lua, 'Mainline/modules/micromenu.lua')
        lua.execute('''
            local m = addon.modules.MenuModule
            m.frames, m.text, m.bgTexture = {}, {}, {}
            m.ApplyCombatState = noop
            m:CreateFrames()
            assert(m.frames.house == nil)
            local _, defaults = m:GetDefaultOptions()
            assert(not defaults.house)
        ''')

    def test_roster_response_does_not_send_another_request(self):
        for file in ('Mainline/modules/micromenu.lua', 'Classic/modules/micromenu.lua'):
            with self.subTest(file=file):
                lua = self.runtime()
                self.load(lua, file)
                lua.execute('''
                    local m = addon.modules.MenuModule
                    m.text, m.bgTexture = {guild = widget}, {guild = widget}
                    m:UpdateGuildText("GUILD_ROSTER_UPDATE")
                    assert(requests == 0, "roster response must not request another roster")
                    m:UpdateGuildText()
                    m:UpdateGuildText("CHAT_MSG_GUILD")
                    assert(requests == 1, "requests must be throttled across refreshes")
                ''')

if __name__ == '__main__':
    unittest.main()
