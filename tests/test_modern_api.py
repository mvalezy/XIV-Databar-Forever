"""Run real module methods in Lua 5.1 with only the WoW seams stubbed.

Run: python -m unittest discover -s tests -p 'test_modern_api.py' -v
Requires lupa.lua51; does not require a running WoW client.
"""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class ModernAPITests(unittest.TestCase):
    def runtime(self, api_mode="modern"):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('''
            function noop() end
            local Frame = {}
            for _, method in ipairs({"SetFont", "SetTextColor", "SetPoint",
                "ClearAllPoints", "SetTexture", "SetTexCoord", "SetVertexColor",
                "SetFrameStrata", "EnableMouse", "RegisterForClicks"}) do
                Frame[method] = noop
            end
            function Frame:Show() self.shown = true end
            function Frame:Hide() self.shown = false end
            function Frame:IsVisible() return self.shown end
            function Frame:SetText(text) self.text = text end
            function Frame:GetStringWidth() return #(self.text or "") end
            function Frame:GetWidth() return self.width or 0 end
            function Frame:SetWidth(width) self.width = width end
            function Frame:SetSize(width, height) self.width, self.height = width, height end
            function Frame:SetID(id) self.id = id end
            function Frame:GetID() return self.id end
            function Frame:SetScript(event, callback) self[event] = callback end
            function CreateFrame() return setmetatable({}, {__index = Frame}) end
            Frame.CreateTexture = CreateFrame
            Frame.CreateFontString = CreateFrame

            GameTooltip = {lines = {}, doubleLines = {}, GetBackdrop = noop,
                SetOwner = noop, ClearLines = noop, Show = noop, Hide = noop,
                IsOwned = function() return false end}
            function GameTooltip:AddLine(text) table.insert(self.lines, text) end
            function GameTooltip:AddDoubleLine(left, right) self.doubleLines[left] = right end
            C_AddOns = {IsAddOnLoaded = function() return false end}
            function InCombatLockdown() return false end
            function GetLootSpecialization() return 0 end
            function SetLootSpecialization(id) chosenLootSpec = id end
            function GetNumSpecializations() return 2 end
            currentSpec = 2
            function specIndex() return currentSpec end
            function specInfo(index)
                assert(type(index) == "number", "specialization index must be a number")
                assert(index == 1 or index == 2, "invalid specialization index")
                return 100 + index, "Spec" .. index
            end
            function coinTexture(amount) return "coins:" .. amount end
            C_SpecializationInfo = {GetSpecialization = specIndex,
                GetSpecializationInfo = specInfo,
                SetSpecialization = function(id) chosenSpec = id end}
            C_CurrencyInfo = {GetCoinTextureString = coinTexture}
            C_ClassTalents = {
                GetConfigIDsBySpecID = function(id)
                    assert(id == 102, "loadout must use the specialization ID")
                    return {7}
                end,
                GetLastSelectedSavedConfigID = function() return 7 end}
            C_Traits = {GetConfigInfo = function() return {ID = 7, name = "Loadout"} end}
            TALENT_FRAME_DROP_DOWN_DEFAULT = "Default"
            SPECIALIZATION = "Specialization"
            addon = {
                L = setmetatable({}, {__index = function(_, key) return key end}),
                constants = {popupPadding = 3, mediaPath = "media/", playerClass = "WARRIOR"},
                db = {profile = {
                    modules = {talent = {enabled = true, loadoutSwitcherEnabled = true,
                        minWidth = 10, showTooltip = true},
                        gold = {showSmallCoins = true, shortThousands = false}},
                    text = {fontSize = 12},
                    general = {barPadding = 2, barPosition = "TOP"}}},
                miniTextPosition = "BOTTOM", modules = {}}
            function addon:NewModule(name)
                local module = {RegisterEvent = noop, RegisterMessage = noop}
                function module:Disable() self.disabled = true end
                self.modules[name] = module
                return module
            end
            addon.GetFrame = CreateFrame
            addon.RegisterFrame = noop
            addon.RegisterMouseoverHoldFrame = noop
            function addon:GetFont() return "font", 12 end
            function addon:GetColor() return 1, 1, 1, 1 end
            function addon:HoverColors() return {1, 1, 1, 1} end
            function addon:GetHeight() return 20 end
            function addon:ApplyModuleFreePlacement() return true end
            function addon:ShouldShowTooltip() return true end
        ''')
        if api_mode == "both":
            lua.execute('''
                function obsolete() error("legacy global used instead of namespace") end
                GetSpecialization = obsolete
                GetSpecializationInfo = obsolete
                GetCoinTextureString = obsolete
            ''')
        elif api_mode in ("legacy", "empty_namespaces"):
            lua.execute('''
                GetSpecialization = specIndex
                GetSpecializationInfo = specInfo
                GetCoinTextureString = coinTexture
                C_SpecializationInfo.GetSpecialization = nil
                C_SpecializationInfo.GetSpecializationInfo = nil
                C_CurrencyInfo = {}
            ''')
            if api_mode == "legacy":
                lua.execute('C_SpecializationInfo = nil; C_CurrencyInfo = nil')
        return lua

    def load(self, lua, path):
        lua.execute((ROOT / path).read_text(), "XIV_Databar_Continued", lua.globals().addon)

    def test_gold_tooltip_uses_ruleset_realm(self):
        lua = self.runtime()
        lua.execute('''
            addon.compat = {isMainline = true}
            addon.constants.playerName, addon.constants.playerRealm = "Tester", "PvP"
            addon.db.global = {characters = {["Tester-PvP"] = {
                realm = "PvP", currentMoney = 20000, sessionMoney = 0, dailyMoney = 0}}}
            function GetRealmName() return nil end
            function UnitName() return "Tester" end
            BONUS_ROLL_REWARD_MONEY, TOTAL = "Gold", "Total"
            floor, abs = math.floor, math.abs
        ''')
        self.load(lua, "Core/modules/gold.lua")
        lua.execute('''
            addon.modules.GoldModule:ShowTooltipMainline()
            assert(GameTooltip.doubleLines.Tester == "coins:20000")
        ''')

    def test_gold_without_legacy_global(self):
        for mode in ("modern", "both", "empty_namespaces", "legacy"):
            with self.subTest(mode=mode):
                lua = self.runtime(mode)
                self.load(lua, "Core/modules/gold.lua")
                lua.execute('assert(addon.modules.GoldModule:FormatGold(12345) == "coins:12345")')

    def test_talent_namespace_preference_and_legacy_fallback(self):
        for mode in ("both", "empty_namespaces", "legacy"):
            with self.subTest(mode=mode):
                lua = self.runtime(mode)
                self.load(lua, "Mainline/modules/talent.lua")
                lua.execute('''
                    local talent = addon.modules.TalentModule
                    talent:OnInitialize()
                    talent:OnEnable()
                    assert(talent.currentSpecID == 2)
                    assert(talent.specText.text == "SPEC2")
                ''')

    def test_talent_without_legacy_globals(self):
        lua = self.runtime()
        self.load(lua, "Mainline/modules/talent.lua")
        lua.execute('''
            assert(GetSpecialization == nil and GetSpecializationInfo == nil)
            local talent = addon.modules.TalentModule
            talent:OnInitialize()
            talent:OnEnable()
            assert(talent.currentSpecID == 2)
            assert(talent.specText.text == "SPEC2")
            assert(talent.loadoutText.text == "Loadout")
            assert(talent.specButtons[1] and talent.specButtons[2])
            assert(talent.lootSpecButtons[1].text.text == "Spec1")
            talent:ShowTooltip()
            assert(GameTooltip.doubleLines.CURRENT_LOOT_SPECIALIZATION == "|cFFFFFFFFSpec2|r")
            local selected = talent.lootSpecButtons[1]
            selected.OnClick(selected, "LeftButton")
            assert(chosenLootSpec == 101)
            local current = talent.lootSpecButtons[0]
            current.OnClick(current, "LeftButton")
            assert(chosenLootSpec == 102)
        ''')


if __name__ == "__main__":
    unittest.main()
