ACTION_TYPE = {
    SKILL = 0,
    ITEM = 1,
    ATTACK = 2,
    DEF = 3,
    ESCAPE = 4,
    MOVE = 5,
    PET = 6,
    NONE = 7,
    EQUIP = 8,
    REBIRTH = 9,
    PET_SKILL = 10,
};

BATTLE_TYPE = {
    NONE = 0,             -- 无
    P_vs_E = 1,           -- 玩家对手
    P_vs_P = 2,           -- 玩家对战
    WATCH = 3,            -- 观战
    ANCHORAGE_BATTLE = 4, -- 站街怪物
    BOSS_BATTLE = 5,      -- 头目
    LASTBOSS_BATTLE = 6,  -- 老大
}

B_TARGET_FLAGS = {
    WHO = 0x1,
    DEAD = 0x2,
    PET = 0x4,
    ME = 0x8,
    FRIEND = 0x10,
    ENEMY = 0x20,
    SOLO = 0x40,
    MULTI = 0x80,
    SIDE = 0x100,
    ALL = 0x200,
    CHECK_WEAPON = 0x400,
    NOT_ME = 0x800,
    LINE = 0x10000,
    TWO = 0x20000,
    TWO_MULTI = 0x40000,
};

local _loadfile = loadfile;

local ctx = {};

---安全执行lua文件
function dofile_s(file)
    if file == "" || file == nil then
        return nil;
    end
    local s, m = pcall(function()
        local fn, msg = _loadfile(file, "bt", ctx);
        if fn then
            return fn();
        end
        error(msg);
    end);
    if s then
        return m;
    end
    print("Error dofile_s: ", m);
    LogToFile("Error dofile_s: " .. m);
    return nil;
end

---@param tbl number[]
---@return number
function FindMax(tbl)
    local mx = nil;
    for key, value in pairs(tbl) do
        if mx == nil then
            mx = value;
        else
            if mx < value then
                mx = value
            end
        end
    end
    return mx;
end

---@param tbl number[]
---@return number
function FindMaxIndex(tbl)
    local mx = nil;
    local ix = -1;
    for key, value in pairs(tbl) do
        if mx == nil then
            mx = value;
            ix = tonumber(key);
        else
            if mx < value then
                mx = value
                ix = tonumber(key);
            end
        end
    end
    return ix;
end

---@param playerData CHARA_DATA
---@return PET_INFO
function GetBattlePet(playerData)
    local petList = playerData.petList;
    ---@type PET_INFO|nil
    local pet = nil;
    for i = 1, 5 do
        if (petList[i] and petList[i].petBattleState == 2) then
            pet = petList[i];
            break;
        end
    end
    return pet;
end

---PS:会过滤不能使用的技能
---@param pet PET_INFO
---@param techId number
---@return PET_TECH @
function GetPetTechByTechId(pet, techId)
    local techList = pet.techList;
    for i = 1, 10 do
        local tech = techList[i];
        if tech and tech.techId == techId and tech.canUse and (tech.field == 0 or tech.field == 1) then
            return tech;
        end
    end
    return nil;
end

---PS:会过滤不能使用的技能
---@param pet PET_INFO
---@param name string
---@return PET_TECH @
function GetPetTechByName(pet, name)
    local techList = pet.techList;
    for i = 1, 10 do
        local tech = techList[i];
        if tech and tech.name == name and tech.canUse and (tech.field == 0 or tech.field == 1) then
            return tech;
        end
    end
    return nil;
end

---PS:会过滤不能使用的技能
---@param pet PET_INFO
---@param fn fun(tech:PET_TECH):boolean
---@return PET_TECH @
function GetPetTechByMatch(pet, fn)
    local techList = pet.techList;
    for i = 1, 10 do
        local tech = techList[i];
        if tech and fn(tech) and tech.canUse and (tech.field == 0 or tech.field == 1) then
            return tech;
        end
    end
    return nil;
end

---@param playerData CHARA_DATA
---@param name string
---@return ITEM_DATA @
function FindItemByName(playerData, name)
    local itemList = playerData.itemList;
    for i = 9, 28 do
        local item = itemList[i];
        if item then
            if item.name == name then
                return item;
            end
        end
    end
    return nil;
end

---@param playerData CHARA_DATA
---@param id number
---@return ITEM_DATA @
function FindItemById(playerData, id)
    local itemList = playerData.itemList;
    for i = 9, 28 do
        local item = itemList[i];
        if item then
            if item.itemId == id then
                return item;
            end
        end
    end
    return nil;
end

---@param playerData CHARA_DATA
---@param fn fun(item:ITEM_DATA):boolean
---@return ITEM_DATA @
function FindItemByMatch(playerData, fn)
    local itemList = playerData.itemList;
    for i = 9, 28 do
        local item = itemList[i];
        if item then
            if fn(item) then
                return item;
            end
        end
    end
    return nil;
end

---@param playerData CHARA_DATA
---@param name string
---@return SKILL_INFO @
function FindSkillByName(playerData, name)
    local skillList = playerData.skillList;
    -- LogToFile("Start Found Skill " .. name);
    for i = 1, 15 do
        local skill = skillList[i];
        -- if skill then
        --     LogToFile(string.format("Skill %d %s %s %d", i, skill.name, skill.canUse, skill.index));
        -- end
        if skill && skill.canUse && skill.name == name then
            return skill;
        end
    end
    return nil;
end

---@param playerData CHARA_DATA
---@param fn fun(skill:SKILL_INFO):boolean
---@return SKILL_INFO @
function FindSkillByMatch(playerData, fn)
    local skillList = playerData.skillList;
    for i = 1, 15 do
        local skill = skillList[i];
        if skill && skill.canUse && fn(skill) then
            return skill;
        end
    end
    return nil;
end

---查找最优的目标
---@param battle BATTLE_INFO
---@param attacker number
---@param techTarget B_TARGET_FLAGS target参数
---@param fn fun(BATTLE_ENTRY):number 目标权重
---@return integer @目标，0开始，-1为找不到
function FindBestTarget(battle, attacker, techTarget, fn)
    local all = bit.band(techTarget, B_TARGET_FLAGS.ALL) != 0
    if (all) then
        return TakeRandomTarget(attacker, techTarget);
    end
    local score = {};
    local enemy = bit.band(techTarget, B_TARGET_FLAGS.ENEMY) != 0
    local friend = bit.band(techTarget, B_TARGET_FLAGS.FRIEND) != 0

    local multiTargets = {
        { 0, 1, 2, 5 }, { 1, 0, 3, 6 }, { 2, 0, 4, 7 }, { 3, 1, 8 }, { 4, 2, 9 },
        { 5, 6, 7, 0 }, { 6, 4, 8, 1 }, { 7, 5, 9, 2 }, { 8, 6, 3 }, { 9, 7, 4 },
        { 10, 11, 12, 15 }, { 11, 10, 13, 16 }, { 12, 10, 14, 17 }, { 13, 11, 18 }, { 14, 12, 19 },
        { 15, 16, 17, 10 }, { 16, 14, 18, 11 }, { 17, 15, 19, 12 }, { 18, 16, 13 }, { 19, 17, 14 },
    };
    local multiTargets2 = {
        { 0, 1, 2, 5, 6, 7 }, { 1, 0, 3, 6, 5, 8 }, { 2, 0, 4, 7, 9, 5 }, { 3, 1, 8, 6 }, { 4, 2, 9, 7 },
        { 5, 6, 7, 0, 1, 2 }, { 6, 4, 8, 1, 0, 3 }, { 7, 5, 9, 2, 0, 4 }, { 8, 6, 3, 1 }, { 9, 7, 4, 2 },
        { 10, 11, 12, 15, 16, 17 }, { 11, 10, 13, 16, 15, 18 }, { 12, 10, 14, 17, 19, 15 }, { 13, 11, 18, 16 }, { 14, 12, 19, 17 },
        { 15, 16, 17, 10, 11, 12 }, { 16, 14, 18, 11, 10, 13 }, { 17, 15, 19, 12, 10, 14 }, { 18, 16, 13, 11 }, { 19, 17, 14, 12 },
    };
    local sideTargets = {
        { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9 },
        { 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 },
    }
    local lineTargets = {
        { 0,  1,  2,  3,  4 }, { 5, 6, 7, 8, 9 },
        { 10, 11, 12, 13, 14 }, { 15, 16, 17, 18, 19 },
    }
    local twoTargets = {
        { 0,  5 }, { 1, 6 }, { 2, 7 }, { 3, 8 }, { 4, 9 },
        { 10, 15 }, { 11, 16 }, { 12, 17 }, { 13, 18 }, { 14, 19 }
    }
    local entryList = battle.entryList;
    local multi = bit.band(techTarget, B_TARGET_FLAGS.MULTI) != 0
    if multi then
        local tMin = 1;
        local tMax = 20;
        if ! friend then
            tMin = 11;
        end
        if ! enemy then
            tMax = 10;
        end
        for i = tMin, tMax do
            local n = score[i] or 0;
            for _, value in ipairs(multiTargets[i]) do
                if entryList[value + 1] then
                    n = n + fn(entryList[value + 1]);
                end
            end
        end
        return FindMaxIndex(score) - 1;
    end
    local multi2 = bit.band(techTarget, B_TARGET_FLAGS.TWO_MULTI) != 0
    if multi2 then
        local tMin = 1;
        local tMax = 20;
        if ! friend then
            tMin = 11;
        end
        if ! enemy then
            tMax = 10;
        end
        for i = tMin, tMax do
            local n = score[i] or 0;
            for _, value in ipairs(multiTargets2[i]) do
                if entryList[value + 1] then
                    n = n + fn(entryList[value + 1]);
                end
            end
        end
        return FindMaxIndex(score) - 1;
    end
    local side = bit.band(techTarget, B_TARGET_FLAGS.SIDE) != 0
    if side then
        local tMin = 1;
        local tMax = 2;
        if ! friend then
            tMin = 2;
        end
        if ! enemy then
            tMax = 1;
        end
        for i = tMin, tMax do
            local n = score[i] or 0;
            for _, value in ipairs(sideTargets[i]) do
                if entryList[value + 1] then
                    n = n + fn(entryList[value + 1]);
                end
            end
        end
        return (FindMaxIndex(score) - 1) * 10;
    end
    local line = bit.band(techTarget, B_TARGET_FLAGS.LINE) != 0
    if line then
        local tMin = 1;
        local tMax = 4;
        if ! friend then
            tMin = 3;
        end
        if ! enemy then
            tMax = 2;
        end
        for i = tMin, tMax do
            local n = score[i] or 0;
            for _, value in ipairs(lineTargets[i]) do
                if entryList[value + 1] then
                    n = n + fn(entryList[value + 1]);
                end
            end
        end
        return (FindMaxIndex(score) - 1) * 5;
    end
    local two = bit.band(techTarget, B_TARGET_FLAGS.TWO) != 0
    if two then
        local tMin = 1;
        local tMax = 10;
        if ! friend then
            tMin = 5;
        end
        if ! enemy then
            tMax = 6;
        end
        for i = tMin, tMax do
            local n = score[i] or 0;
            for _, value in ipairs(twoTargets[i]) do
                if entryList[value + 1] then
                    n = n + fn(entryList[value + 1]);
                end
            end
        end
        local maxIndex = FindMaxIndex(score) % (#twoTargets + 1)
        if entryList[twoTargets[maxIndex][1] + 1] then
            return twoTargets[maxIndex][1];
        else
            return twoTargets[maxIndex][2];
        end
    end
    return -1;
end

SCORE_CALCER = {
    ---@param entry BATTLE_ENTRY
    FriendLiveByCount = function(entry)
        if entry && entry.hp > 0 && entry.battlePos < 10 then
            return 1;
        end
        return 0;
    end,
    ---@param entry BATTLE_ENTRY
    FriendHeath50ByCount = function(entry)
        if entry && entry.hp > 0 && entry.hp < entry.maxHp * 0.5 && entry.battlePos < 10 then
            return 1;
        end
        return 0;
    end,
    ---@param entry BATTLE_ENTRY
    FriendDeathByCount = function(entry)
        if entry && entry.hp <= 0 && entry.battlePos < 10 then
            return 1;
        end
        return 0;
    end,
    ---@param entry BATTLE_ENTRY
    EnemyByCount = function(entry)
        if entry && entry.hp > 0 && entry.battlePos >= 10 then
            return 1;
        end
        return 0;
    end,
}

---@param battleInfo BATTLE_INFO
---@param playerData CHARA_DATA
function AutoBattleEvent_SIMPLE(battleInfo, playerData)
    ---@type table<ACTION_TYPE, fun(BATTLE_ACTION:BATTLE_ACTION)>
    local actions;
    local pet = GetBattlePet(playerData);
    local petPosition = playerData.position + 5;
    if petPosition >= 10 then
        petPosition = petPosition - 10;
    end
    local entryList = battleInfo.entryList;
    local canUseSkill = true;
    actions = {
        ---@param action BATTLE_ACTION
        [ACTION_TYPE.ATTACK] = function(action)
            if action.target < 0 then
                battleInfo.SendAction(ACTION_TYPE.ATTACK, -1);
                return;
            end
            local entry = entryList[action.target + 1];
            if battleInfo.CHK_TARGET_AUTO or entry == nil or entry.hp <= 0 then
                if playerData.weaponBoomerang then
                    local target = FindBestTarget(battleInfo, playerData.position,
                        bit.bor(B_TARGET_FLAGS.ENEMY, B_TARGET_FLAGS.LINE), SCORE_CALCER.EnemyByCount);
                    battleInfo.SendAction(ACTION_TYPE.ATTACK, target);
                    return;
                elseif playerData.weaponKnife then
                    local target = FindBestTarget(battleInfo, playerData.position,
                        bit.bor(B_TARGET_FLAGS.ENEMY, B_TARGET_FLAGS.TWO), SCORE_CALCER.EnemyByCount);
                    battleInfo.SendAction(ACTION_TYPE.ATTACK, target);
                    return;
                end
            end
            if entry == nil or entry.hp <= 0 then
                battleInfo.SendAction(ACTION_TYPE.ATTACK, -1);
            else
                battleInfo.SendAction(ACTION_TYPE.ATTACK, action.target);
            end
        end,
        ---@param action BATTLE_ACTION
        [ACTION_TYPE.SKILL] = function(action)
            if canUseSkill ~= true then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local skillList = playerData.skillList;
            local skill = nil;
            for i = 1, 15 do
                skill = skillList[i];
                if (skill and skill.skillId == action.skillId) then
                    break;
                end
            end
            if skill == nil then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local techList = skill.techList;
            ---@type SKILL_TECH
            local tech = nil;
            local techId = -1;
            local skillLv = action.techId + 1;
            if battleInfo.CHK_SKILL_LV_AUTO then
                skillLv = 15;
            end
            for i = skillLv, 1, -1 do
                tech = techList[i];
                if tech and tech.canUse and (tech.field == 1 or tech.field == 0) and tech.fp <= playerData.fp then
                    techId = i - 1;
                    break;
                end
                tech = nil;
            end
            if tech == nil then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local techHead = math.floor(techId / 100);
            ---@type number
            local techTarget = tech.target;
            local target = action.target;
            if techHead == 260 then
                --一石二鸟
                techTarget = bit.bor(techTarget, B_TARGET_FLAGS.TWO);
            elseif techHead == 259 || techHead == 9 then
                --毒击 阳炎
                if playerData.weaponBoomerang then
                    techTarget = bit.bor(techTarget, B_TARGET_FLAGS.LINE);
                end
                if playerData.weaponKnife then
                    techTarget = bit.bor(techTarget, B_TARGET_FLAGS.TWO);
                end
            elseif techHead == 2005 then
                --追月
                techTarget = bit.bor(techTarget, B_TARGET_FLAGS.TWO_MULTI);
            elseif techHead == 404 || techHead == 406 || techHead == 267 || techHead == 266 then
                --因果报应 精神冲击波 人宠合击
                if bit.bor(techTarget, B_TARGET_FLAGS.ALL) == 0 then
                    techTarget = bit.bor(techTarget, B_TARGET_FLAGS.TWO_MULTI);
                end
            end
            local entry = entryList[action.target + 1];
            if battleInfo.CHK_TARGET_AUTO or entry == nil or entry.hp <= 0 then
                local scorer = SCORE_CALCER.EnemyByCount;
                if bit.band(techTarget, B_TARGET_FLAGS.ENEMY) == 0 then
                    if bit.band(techTarget, B_TARGET_FLAGS.DEAD) == 0 then
                        scorer = SCORE_CALCER.FriendLiveByCount;
                    else
                        scorer = SCORE_CALCER.FriendDeathByCount;
                    end
                end
                target = FindBestTarget(battleInfo, playerData.position, techTarget, scorer);
            end
            battleInfo.SendAction(ACTION_TYPE.SKILL, action.skillId, techId, target);
        end,
        ---@param action BATTLE_ACTION
        [ACTION_TYPE.PET_SKILL] = function(action)
            local target = action.target;
            if pet == nil then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local tech = GetPetTechByTechId(pet, action.techId);
            local techId = -1;
            if tech != nil && tech.fp <= entryList[petPosition + 1].fp then
                techId = tech.techId;
            end
            if techId < 0 or tech == nil then
                target = TakeRandomTarget(petPosition, B_TARGET_FLAGS.ENEMY);
                battleInfo.SendAction(ACTION_TYPE.PET_SKILL, 7300, target);
                return
            end
            if battleInfo.CHK_TARGET_AUTO || entryList[target + 1] == nil || entryList[target + 1].hp <= 0 then
                if bit.band(tech.target, B_TARGET_FLAGS.DEAD) == 0 then
                    target = TakeRandomTarget(petPosition, tech.target);
                end
            end
            battleInfo.SendAction(ACTION_TYPE.PET_SKILL, techId, target);
        end,
        ---@param action BATTLE_ACTION
        [ACTION_TYPE.ITEM] = function(action)
            if canUseSkill ~= true then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local item = FindItemById(playerData, action.itemId);
            if item == nil then
                actions[ACTION_TYPE.ATTACK]({ target = -1 });
                return;
            end
            local target = action.target;
            if entryList[target + 1] == nil then
                target = TakeRandomTarget(playerData.position, item.target);
            end
            battleInfo.SendAction(ACTION_TYPE.ITEM, item.itemId, action.target);
        end,
        [ACTION_TYPE.ESCAPE] = function(action)
            battleInfo.SendAction(ACTION_TYPE.ESCAPE, -1, -1, -1);
        end,
        [ACTION_TYPE.DEF] = function(action)
            battleInfo.SendAction(ACTION_TYPE.DEF, -1, -1, -1);
        end,
    }
    local SendAction = battleInfo.SendAction;
    battleInfo.SendAction = function(...)
        print("battleInfo.SendAction", ...);
        SendAction(...);
    end
    if battleInfo.CHK_STOP_DEATH then
        for i = 1, 10 do
            local entry = entryList[i];
            if entry && entry.hp <= 0 then
                return 0;
            end
        end
    end
    if battleInfo.CHK_STOP_LOST_PARTY then
        local cnt = 0;
        for i = 1, 10 do
            local entry = entryList[i];
            if entry then
                cnt = cnt + 1;
                return 0;
            end
        end
        if cnt != battleInfo.partyCount then
            return 0;
        end
    end
    if battleInfo.CHK_STOP_BAG_FULL then
        local itemList = playerData.itemList;
        local cnt = 0;
        for i = 9, 28 do
            local item = itemList[i];
            if item then
                cnt = cnt + 1;
                return 0;
            end
        end
        if cnt == 20 then
            return 0;
        end
    end
    if battleInfo.battleType == BATTLE_TYPE.BOSS_BATTLE || battleInfo.battleType == BATTLE_TYPE.LASTBOSS_BATTLE then
        if battleInfo.CHK_STOP_BOSS then
            return 0;
        end
    end
    if battleInfo.CHK_STOP_LV1 then
        for i = 11, 20 do
            if entryList[i] && entryList[i].lv == 1 && battleInfo.CHK_STOP_LV1 then
                return 0;
            end
        end
    end
    if battleInfo.CHK_REC_ITEM || battleInfo.CHK_REC_SKILL then
        -- if battleInfo.lastAction[1].type != ACTION_TYPE.PET_SKILL then
        local targetLHp = -1;
        for i = 1, 10 do
            local entry = entryList[i];
            if entry && entry.hp > 0 && entry.hp < entry.maxHp * 0.5 then
                if targetLHp < 0 || (entry.hp / entry.maxHp) < (entryList[targetLHp + 1].hp / entryList[targetLHp + 1].maxHp) then
                    targetLHp = i - 1;
                end
            end
        end
        if targetLHp >= 0 then
            if battleInfo.CHK_REC_ITEM then
                local item = FindItemByMatch(playerData, function(item)
                    if item && item.battleUseFlag != 0 then
                        if string.find(item.name, "生命力回复药") != nil then
                            return true;
                        end
                    end
                    return false;
                end)
                if item != nil then
                    battleInfo.CHK_TARGET_AUTO = false;
                    actions[ACTION_TYPE.ITEM]({ itemId = item.itemId, target = targetLHp });
                    canUseSkill = false;
                end
            end
            if battleInfo.CHK_REC_SKILL then
                if canUseSkill then
                    local ar = 60;
                    local skill = FindSkillByName(playerData, "补血魔法");
                    if skill == nil then
                        ar = 36;
                        skill = FindSkillByName(playerData, "强力补血魔法");
                    end
                    if skill == nil then
                        ar = 24;
                        skill = FindSkillByName(playerData, "超强补血魔法");
                    end
                    -- if skill then
                    --     LogToFile(string.format("Found Skill %s %s", skill.name, skill.canUse))
                    -- else
                    --     LogToFile(string.format("Not Found Skill "))
                    -- end
                    if skill && skill.canUse then
                        local dhp = entryList[targetLHp + 1].maxHp - entryList[targetLHp + 1].hp;
                        local dlv = math.floor((dhp + ar - 1) / ar) + 1;
                        if dlv < 0 then
                            dlv = 1;
                        elseif dlv >= 15 then
                            dlv = 15;
                        end
                        local tech = nil;
                        local techList = skill.techList;
                        for i = 15, 1, -1 do
                            local t = techList[i];
                            if t && t.canUse && t.fp <= playerData.fp then
                                if i >= dlv || tech == nil then
                                    tech = i - 1;
                                end
                            end
                        end
                        if tech != nil then
                            battleInfo.CHK_TARGET_AUTO = false;
                            actions[ACTION_TYPE.SKILL]({ skillId = skill.skillId, techId = tech, target = targetLHp });
                            canUseSkill = false;
                        end
                    end
                end
            end
            if ! canUseSkill then
                goto ACTION_2;
            end
            -- end
        end
    end
    print(battleInfo.lastAction[1].type)
    if actions[battleInfo.lastAction[1].type] then
        actions[battleInfo.lastAction[1].type](battleInfo.lastAction[1]);
    else
        actions[ACTION_TYPE.ATTACK]({ target = -1 });
    end
    ::ACTION_2::
    print(battleInfo.lastAction[2].type)
    if actions[battleInfo.lastAction[2].type] then
        actions[battleInfo.lastAction[2].type](battleInfo.lastAction[2]);
    else
        actions[ACTION_TYPE.ATTACK]({ target = -1 });
    end
    return 1;
end

---@param battleInfo BATTLE_INFO
---@param playerData CHARA_DATA
function AutoBattleEvent(battleInfo, playerData)
    print(battleInfo, playerData);
    if (battleInfo.CHK_TYPE_SIMPLE) then
        local s, m = pcall(AutoBattleEvent_SIMPLE, battleInfo, playerData);
        if s then
            return m;
        else
            print("ERROR: AutoBattleEvent_SIMPLE ", m);
            LogToFile("ERROR: AutoBattleEvent_SIMPLE " .. m);
            return 0;
        end
    else
        local fn = dofile_s("lua/autobattle.lua");
        if fn then
            local s, m = pcall(fn, battleInfo, playerData);
            if s then
                return m;
            else
                print("ERROR: AutoBattleEvent_LUA ", m);
                LogToFile("ERROR: AutoBattleEvent_LUA " .. m);
                return 0;
            end
        end
    end
    return 0;
end

for key, value in pairs(_G) do
    ctx[key] = value;
end

ctx.dofile = nil;
ctx.loadfile = nil;
ctx.load = nil;
ctx.AutoBattleEvent_SIMPLE = nil;
ctx.AutoBattleEvent = nil;
