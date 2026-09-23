"""Offline regressions: real addon Lua in Lua 5.1, not a WoW client.
Run: python3 -m unittest discover -s tests -v (requires lupa==2.8).
"""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]


class ForeverTests(unittest.TestCase):
    def runtime(self, interface=16001, project=1):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('''
            WOW_PROJECT_MAINLINE = 1
            WOW_PROJECT_CLASSIC = 2
            WOW_PROJECT_BURNING_CRUSADE_CLASSIC = 5
            WOW_PROJECT_WRATH_CLASSIC = 11
            WOW_PROJECT_CATACLYSM_CLASSIC = 14
            WOW_PROJECT_MISTS_CLASSIC = 19
            addon = {}
        ''')
        lua.globals().WOW_PROJECT_ID = project
        lua.execute(f'function GetBuildInfo() return "1.60.1", "69977", "", {interface} end')
        lua.execute((ROOT / 'Core/compat.lua').read_text(), 'XIV_Databar_Continued', lua.globals().addon)
        return lua

    def load_core(self, lua):
        lua.execute('''
            local lib = {}
            testLibrary = lib
            function lib:NewAddon() end
            function lib:GetLocale() return {} end
            function lib:NewDataObject() end
            LibStub = setmetatable({GetLibrary = function() return lib end},
                {__call = function() return lib end})
            function UnitName() return "Tester" end
            function UnitClass() return "Warrior", "WARRIOR" end
            function UnitLevel() return 10 end
            function UnitFactionGroup() return "Alliance", "Alliance" end
            function GetRealmName() return nil end
            function hooksecurefunc() end
        ''')
        lua.execute((ROOT / 'core.lua').read_text(), 'XIV_Databar_Continued', lua.globals().addon)

    def test_initialization_uses_acedb_realm_for_character_storage(self):
        lua = self.runtime()
        self.load_core(lua)
        lua.execute('''
            function noop() end
            function testLibrary:New()
                return {keys = {char = "Tester - PvP", realm = "PvP"}, RegisterDefaults = noop}
            end
            testLibrary.MediaType = {FONT = "font"}
            testLibrary.Register = noop
            addon.SetupOptions, addon.RegisterChatCommand = noop, noop
            C_Timer = {After = noop}
            addon:OnInitialize()
            assert(addon.constants.playerRealm == "PvP", "gold storage must use the ruleset realm")
        ''')

    def test_character_profile_uses_acedb_ruleset_key(self):
        lua = self.runtime()
        self.load_core(lua)
        lua.execute('''
            addon.db = {keys = {char = "Tester - Hardcore", realm = "Hardcore"}}
            assert(addon:GetCharacterProfileKey() == "Tester - Hardcore")
        ''')

    def test_forever_uses_modern_apis_without_retail_content(self):
        lua = self.runtime()
        lua.execute('''
            assert(addon.compat.isForever == true, "Forever must be detected by interface")
            assert(addon.compat.isMainline, "Forever exposes the modern API")
            assert(addon.compat.isRetail == false, "Retail content is not available on Forever")
            assert(not addon.compat.isClassicEra, "Forever is not Era")
            assert(not addon.compat.features.travel.secondaryPorts)
        ''')

    def test_other_clients_keep_existing_flags(self):
        for interface, project, flag in ((120100, 1, 'isMainline'), (11509, 2, 'isClassicEra'),
                                         (20505, 5, 'isTBC'), (50500, 19, 'isMists')):
            with self.subTest(interface=interface):
                lua = self.runtime(interface, project)
                self.assertTrue(lua.globals().addon.compat[flag])
                self.assertFalse(bool(lua.globals().addon.compat.isForever))


if __name__ == '__main__':
    unittest.main()
