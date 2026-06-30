---@meta _

---记录日志到autobattle.log
function LogToFile(s) end

---@class PET_TECH
---@field use boolean
---@field name string 名字
---@field desc string 技能说明
---@field fp number 耗魔
---@field techId number techId
---@field seqNo number 排序
---@field field number 战斗可用标记，0、1为战斗可用
---@field target number 范围
---@field index number
---@field canUse boolean


---@class PET_INFO
---@field use boolean
---@field lv number
---@field name string
---@field imageNo number
---@field userPetName string
---@field injury number
---@field exp number
---@field nextExp number
---@field petBattleState number 战斗状态 1为待命，2为战斗
---@field hp number
---@field maxHp number
---@field fp number
---@field maxFp number
---@field loyalty number 忠诚
---@field seqNo number 排序
---@field tribe number 排序
---@field techList PET_TECH[] 技能


---@class SKILL_TECH
---@field use boolean
---@field canUse boolean 是否可用
---@field reqLv number
---@field target number
---@field field number
---@field fp number 耗魔
---@field name string 名字
---@field desc string 技能说明

---@class SKILL_INFO
---@field canUse boolean
---@field index number index
---@field skillId number
---@field name string
---@field lv number
---@field exp number
---@field maxLv number
---@field nextExp number
---@field reqSlot number 占用栏数
---@field seqNo number 排序
---@field fpReduce number
---@field techList SKILL_TECH[]


---@class CHARA_DATA
---@field hp number
---@field maxHp number
---@field fp number
---@field maxFp number
---@field lv number
---@field name string
---@field imageNo number
---@field exp number
---@field nextExp number
---@field injury number
---@field penalty number
---@field position number
---@field gold number
---@field feverTime number
---@field surprisal number @0为普通，1偷袭，2被偷袭
---@field disableAct1 boolean
---@field disableAct2 boolean
---@field disablePetAct1 boolean
---@field disablePetAct2 boolean
---@field hasPet boolean
---@field weaponDirect boolean
---@field weaponBow boolean
---@field weaponBoomerang boolean
---@field weaponKnife boolean
---@field petRide boolean
---@field skillList SKILL_INFO[]
---@field itemList ITEM_DATA[]
---@field petList PET_INFO[]

---@class ITEM_DATA
---@field use boolean
---@field lv number
---@field name string
---@field imageNo number
---@field memo string
---@field desc string
---@field itemId number
---@field count number
---@field target number
---@field itemType number
---@field flag number
---@field canUseInField number
---@field battleUseFlag number
---@field color number

---@class BATTLE_ENTRY
---@field battlePos number
---@field name string
---@field lv number
---@field imageNo number
---@field hp number
---@field fp number
---@field maxHp number
---@field maxFp number
---@field isPlayer boolean
---@field isPet boolean
---@field isDeath boolean
---@field isTwoAction boolean
---@field isPoison boolean
---@field isSleep boolean
---@field isStone boolean
---@field isDrug boolean
---@field isConfusion boolean
---@field isForget boolean

---@class BATTLE_ACTION
---@field type? number
---@field skillId? number
---@field techId? number
---@field target? number
---@field itemId? number

---@class BATTLE_INFO
---@field battleTurn number 战斗回合
---@field battleType BATTLE_TYPE 战斗类型
---@field battleField FIELD_FLAGS 战斗场地效果
---@field entryList BATTLE_ENTRY[] 队形列表
---@field partyCount number 队伍开始数量
---@field lastAction BATTLE_ACTION[] 简单模式下返回最后的操作
---@field CHK_TYPE_SIMPLE boolean 简单模式
---@field CHK_TYPE_LUA boolean LUA模式
---@field CHK_REC_ITEM boolean 使用物品回血
---@field CHK_REC_SKILL boolean 使用技能回血
---@field CHK_STOP_LV1 boolean @1级怪物停止自动战斗
---@field CHK_STOP_BOSS boolean @BOSS怪物停止自动战斗
---@field CHK_STOP_BAG_FULL boolean @满包停止自动战斗
---@field CHK_STOP_LOST_PARTY boolean 丢人停止自动战斗
---@field CHK_STOP_DEATH boolean 死亡停止自动战斗
---@field CHK_TARGET_AUTO boolean 自动选择目标
---@field CHK_TARGET_LAST boolean 优先最后选择目标
---@field CHK_SKILL_LV_AUTO boolean 自动技能等级
---@field CHK_SKILL_LV_LAST boolean 固定技能等级
BATTLE_INFO = {}

---@enum ACTION_TYPE
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

---@alias TARGET_INDEX number
---@alias SKILL_OR_ITEM_INDEX number
---@alias TECH_INDEX number

---@enum BATTLE_TYPE
BATTLE_TYPE = {
    NONE = 0,             -- 无
    P_vs_E = 1,           -- 玩家对手
    P_vs_P = 2,           -- 玩家对战
    WATCH = 3,            -- 观战
    ANCHORAGE_BATTLE = 4, -- 站街怪物
    BOSS_BATTLE = 5,      -- 头目
    LASTBOSS_BATTLE = 6,  -- 老大
}

---@enum FIELD_FLAGS
FIELD_FLAGS = {
    EARTH = 0x1,
    WATER = 0x2,
    FIRE = 0x4,
    WIND = 0x8,
    SILENCE = 0x10,
};

---@enum B_TARGET_FLAGS
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

---安全执行lua文件
---@return any @失败时返回nil, 并记录日志
function dofile_s(file) end

---获取当前时间
---@return number
function GetTime() end

---获取随机目标
---@param attacker number @0-19
---@param techTarget number Tech.target
---@return number @目标序号，0-19
function TakeRandomTarget(attacker, techTarget) end

---检测目标并返回target
---@param attacker number @0-19
---@param defender number @0-19
---@param techTarget number Tech.target
---@return number @目标序号，0-19
function CheckAndGetTarget(attacker, defender, techTarget) end

---@param playerData CHARA_DATA
---@return PET_INFO
function GetBattlePet(playerData) end

---发送战斗指令
---@param type ACTION_TYPE 类型
---@param param1? number SKILL: skillId, ITEM: itemId, ATTACK: target, PET_SKILL: techId, PET: petIndex, EQUIP: invIndex, REBIRTH: state(1:变身,0:取消变身)
---@param param2? number SKILL: techIndex, ITEM: target, PET_SKILL: target,
---@param param3? number SKILL: target
function BATTLE_INFO.SendAction(type, param1, param2, param3) end

---查找最优的目标
---@param battle BATTLE_INFO
---@param attacker number
---@param techTarget B_TARGET_FLAGS target参数
---@param fn fun(BATTLE_ENTRY):number 目标权重
---@return integer @目标，0开始，-1为找不到
function FindBestTarget(battle, attacker, techTarget, fn) end

---@param tbl number[]
---@return number
function FindMax(tbl) end

---@param tbl number[]
---@return number
function FindMaxIndex(tbl) end

---PS:会过滤不能使用的技能
---@param pet PET_INFO
---@param name string
---@return PET_TECH @
function GetPetTechByName(pet, name) end

---PS:会过滤不能使用的技能
---@param pet PET_INFO
---@param fn fun(tech:PET_TECH):boolean
---@return PET_TECH @
function GetPetTechByMatch(pet, fn) end

---@param playerData CHARA_DATA
---@param name string
---@return ITEM_DATA @
function FindItemByName(playerData, name) end

---@param playerData CHARA_DATA
---@param id number
---@return ITEM_DATA @
function FindItemById(playerData, id) end

---@param playerData CHARA_DATA
---@param fn fun(item:ITEM_DATA):boolean
---@return ITEM_DATA @
function FindItemByMatch(playerData, fn) end

---@param playerData CHARA_DATA
---@param name string
---@return SKILL_INFO @
function FindSkillByName(playerData, name) end

---@param playerData CHARA_DATA
---@param fn fun(skill:SKILL_INFO):boolean
---@return SKILL_INFO @
function FindSkillByMatch(playerData, fn) end

---@alias CALCER fun(entry:BATTLE_ENTRY):number

---@class SCORE_CALCER
---@field FriendLiveByCount CALCER
---@field FriendHeath50ByCount CALCER
---@field FriendDeathByCount CALCER
---@field EnemyByCount CALCER
SCORE_CALCER = {}
