#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cap-aware BP distribution for contract summon (per-stat max 62)."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Modules/petSummonContract.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
LOCAL = TEMP / "petSummonContract.lua"
OUT = TEMP / "petSummonContract_bp.lua"

# Replace constants block - remove obsolete ratio constants for mode 1-3, add cap-aware notes
CONST_OLD = """local SUMMON_BP_A_HIGH_MIN = 0.58
local SUMMON_BP_A_HIGH_MAX = 0.72
local SUMMON_BP_B_HIGH_CENTER = 0.40
local SUMMON_BP_B_HIGH_MIN = 0.35
local SUMMON_BP_B_HIGH_MAX = 0.45
local SUMMON_BP_C_HIGH_CENTERS = { 0.48, 0.22, 0.18 }"""

CONST_NEW = """-- 单/双/三高改为按点数分配（尊重单项上限 SUMMON_BP_PER_STAT_CAP）
local SUMMON_BP_SINGLE_HIGH_MIN = 52
local SUMMON_BP_DUAL_HIGH_MIN = { 38, 32 }
local SUMMON_BP_TRIPLE_HIGH_MIN = { 40, 28, 22 }"""

ROLL_TWO_OLD = """function Module:rollTwoHighRatios(targetTotal)
  for _ = 1, 30 do
    local r1 = clampRatio(jitterRatio(SUMMON_BP_B_HIGH_CENTER, SUMMON_BP_JITTER_PCT), SUMMON_BP_B_HIGH_MIN, SUMMON_BP_B_HIGH_MAX)
    local r2 = clampRatio(jitterRatio(SUMMON_BP_B_HIGH_CENTER, SUMMON_BP_JITTER_PCT), SUMMON_BP_B_HIGH_MIN, SUMMON_BP_B_HIGH_MAX)
    local v1 = math.floor(targetTotal * r1)
    local v2 = math.floor(targetTotal * r2)
    if math.abs(v1 - v2) >= SUMMON_BP_HIGH_MIN_GAP and (r1 + r2) < 0.90 then
      return r1, r2
    end
  end
  return 0.42, 0.38
end

function Module:rollThreeHighRatios(targetTotal)
  for _ = 1, 30 do
    local rs = {}
    for i, center in ipairs(SUMMON_BP_C_HIGH_CENTERS) do
      local lo = math.max(0.10, center - 0.08)
      local hi = math.min(0.60, center + 0.08)
      rs[i] = clampRatio(jitterRatio(center, SUMMON_BP_JITTER_PCT), lo, hi)
    end
    table.sort(rs, function(a, b) return a > b end)
    local v1 = math.floor(targetTotal * rs[1])
    local v2 = math.floor(targetTotal * rs[2])
    local v3 = math.floor(targetTotal * rs[3])
    if v1 > v2 and v2 > v3 and (v1 - v2) >= SUMMON_BP_HIGH_MIN_GAP and (v2 - v3) >= SUMMON_BP_HIGH_MIN_GAP then
      return rs[1], rs[2], rs[3]
    end
  end
  return SUMMON_BP_C_HIGH_CENTERS[1], SUMMON_BP_C_HIGH_CENTERS[2], SUMMON_BP_C_HIGH_CENTERS[3]
end"""

CAP_AWARE_FUNCS = """
function Module:bpMinLowPoints(targetTotal)
  return math.max(1, math.floor(targetTotal * SUMMON_BP_FOCUS_LOW_MIN_RATIO))
end

function Module:clampBpPoint(value, targetTotal, minLow)
  local cap = SUMMON_BP_PER_STAT_CAP
  value = math.floor(tonumber(value) or minLow)
  if value < minLow then value = minLow end
  if value > cap then value = cap end
  if value > targetTotal then value = targetTotal end
  return value
end

function Module:splitRemainderEvenly(remain, count, minEach, cap)
  local out = {}
  remain = math.floor(remain)
  minEach = math.max(1, minEach)
  cap = cap or SUMMON_BP_PER_STAT_CAP
  for i = 1, count do
    out[i] = minEach
  end
  remain = remain - minEach * count
  local guard = 0
  while remain > 0 and guard < 10000 do
    guard = guard + 1
    local candidates = {}
    for i = 1, count do
      if out[i] < cap then table.insert(candidates, i) end
    end
    if #candidates == 0 then break end
    local pick = candidates[math.random(1, #candidates)]
    out[pick] = out[pick] + 1
    remain = remain - 1
  end
  return out
end

function Module:buildDistributionPoints(mode, targetTotal)
  local cap = SUMMON_BP_PER_STAT_CAP
  local minLow = self:bpMinLowPoints(targetTotal)
  local ints = { 0, 0, 0, 0, 0 }
  local highSet = {}
  if mode == 1 then
    local highIdx = self:pickHighIndices(1)[1]
    local highMin = math.min(cap, math.max(SUMMON_BP_SINGLE_HIGH_MIN, minLow + 1))
    local highMax = math.min(cap, targetTotal - minLow * 4)
    if highMax < highMin then highMax = highMin end
    local highPts = math.random(highMin, highMax)
    ints[highIdx] = highPts
    highSet[highIdx] = true
    local lows = self:splitRemainderEvenly(targetTotal - highPts, 4, minLow, cap)
    local j = 1
    for i = 1, 5 do
      if i ~= highIdx then
        ints[i] = lows[j]
        j = j + 1
      end
    end
  elseif mode == 2 then
    local highs = self:pickHighIndices(2)
    local h1min = math.min(cap, math.max(SUMMON_BP_DUAL_HIGH_MIN[1], minLow + 1))
    local h2min = math.min(cap, math.max(SUMMON_BP_DUAL_HIGH_MIN[2], minLow + 1))
    local h1max = math.min(cap, targetTotal - minLow * 3 - h2min)
    if h1max < h1min then h1max = h1min end
    local h1 = math.random(h1min, h1max)
    local h2max = math.min(cap, targetTotal - h1 - minLow * 3)
    if h2max < h2min then h2max = h2min end
    local h2 = math.random(h2min, h2max)
    if math.abs(h1 - h2) < SUMMON_BP_HIGH_MIN_GAP then
      if h2 + SUMMON_BP_HIGH_MIN_GAP <= h2max then
        h2 = h2 + SUMMON_BP_HIGH_MIN_GAP
      elseif h1 - SUMMON_BP_HIGH_MIN_GAP >= h1min then
        h1 = h1 - SUMMON_BP_HIGH_MIN_GAP
      end
    end
    ints[highs[1]], ints[highs[2]] = h1, h2
    highSet[highs[1]], highSet[highs[2]] = true, true
    local lows = self:splitRemainderEvenly(targetTotal - h1 - h2, 3, minLow, cap)
    local j = 1
    for i = 1, 5 do
      if not highSet[i] then
        ints[i] = lows[j]
        j = j + 1
      end
    end
  elseif mode == 3 then
    local highs = self:pickHighIndices(3)
    local mins = SUMMON_BP_TRIPLE_HIGH_MIN
    local h1min = math.min(cap, math.max(mins[1], minLow + 1))
    local h2min = math.min(cap, math.max(mins[2], minLow + 1))
    local h3min = math.min(cap, math.max(mins[3], minLow + 1))
    local h1max = math.min(cap, targetTotal - minLow * 2 - h2min - h3min)
    if h1max < h1min then h1max = h1min end
    local h1 = math.random(h1min, h1max)
    local h2max = math.min(cap, targetTotal - h1 - minLow * 2 - h3min)
    if h2max < h2min then h2max = h2min end
    local h2 = math.random(h2min, h2max)
    local h3max = math.min(cap, targetTotal - h1 - h2 - minLow * 2)
    if h3max < h3min then h3max = h3min end
    local h3 = math.random(h3min, h3max)
    local ordered = { h1, h2, h3 }
    table.sort(ordered, function(a, b) return a > b end)
    h1, h2, h3 = ordered[1], ordered[2], ordered[3]
    ints[highs[1]], ints[highs[2]], ints[highs[3]] = h1, h2, h3
    highSet[highs[1]], highSet[highs[2]], highSet[highs[3]] = true, true, true
    local lows = self:splitRemainderEvenly(targetTotal - h1 - h2 - h3, 2, minLow, cap)
    local j = 1
    for i = 1, 5 do
      if not highSet[i] then
        ints[i] = lows[j]
        j = j + 1
      end
    end
  else
    return nil, highSet
  end
  return ints, highSet
end
"""

BUILD_DIST_OLD = """function Module:buildDistributionRatios(mode, targetTotal)
  local ratios = { 0, 0, 0, 0, 0 }
  local highSet = {}
  if mode == 1 then
    local highIdx = self:pickHighIndices(1)[1]
    local center = math.random(SUMMON_BP_A_HIGH_MIN * 100, SUMMON_BP_A_HIGH_MAX * 100) / 100
    local rHigh = clampRatio(jitterRatio(center, SUMMON_BP_JITTER_PCT), SUMMON_BP_A_HIGH_MIN, SUMMON_BP_A_HIGH_MAX)
    local rLow = (1 - rHigh) / 4
    for i = 1, 5 do
      ratios[i] = (i == highIdx) and rHigh or rLow
      if i == highIdx then highSet[i] = true end
    end
  elseif mode == 2 then
    local highs = self:pickHighIndices(2)
    local r1, r2 = self:rollTwoHighRatios(targetTotal)
    local rLow = (1 - r1 - r2) / 3
    if rLow < SUMMON_BP_FOCUS_LOW_MIN_RATIO then
      rLow = SUMMON_BP_FOCUS_LOW_MIN_RATIO
      local scale = (1 - rLow * 3) / (r1 + r2)
      r1, r2 = r1 * scale, r2 * scale
    end
    for i = 1, 5 do ratios[i] = rLow end
    ratios[highs[1]], ratios[highs[2]] = r1, r2
    highSet[highs[1]], highSet[highs[2]] = true, true
  elseif mode == 3 then
    local highs = self:pickHighIndices(3)
    local rh, rm, rl = self:rollThreeHighRatios(targetTotal)
    local rLow = (1 - rh - rm - rl) / 2
    if rLow < SUMMON_BP_FOCUS_LOW_MIN_RATIO then
      rLow = SUMMON_BP_FOCUS_LOW_MIN_RATIO
      local scale = (1 - rLow * 2) / (rh + rm + rl)
      rh, rm, rl = rh * scale, rm * scale, rl * scale
    end
    for i = 1, 5 do ratios[i] = rLow end
    ratios[highs[1]], ratios[highs[2]], ratios[highs[3]] = rh, rm, rl
    highSet[highs[1]], highSet[highs[2]], highSet[highs[3]] = true, true, true
  elseif mode == 4 then"""

BUILD_DIST_NEW = """function Module:buildDistributionRatios(mode, targetTotal)
  local ratios = { 0, 0, 0, 0, 0 }
  local highSet = {}
  if mode == 4 then"""

SPLIT_OLD = """function Module:splitTotalRandom(targetTotal)
  local mode = self:rollDistributionMode()
  local ratios, highSet = self:buildDistributionRatios(mode, targetTotal)
  local ints = {}
  for i = 1, 5 do
    ints[i] = math.floor(targetTotal * ratios[i])
  end
  local minArr, maxArr = self:buildBpBoundsForMode(targetTotal, mode, highSet)
  ints = self:rebalanceBpIntsPerStat(ints, targetTotal, minArr, maxArr)
  return self:applyPerStatCapAndRebalance(ints, targetTotal)
end"""

SPLIT_NEW = """function Module:splitTotalRandom(targetTotal)
  local mode = self:rollDistributionMode()
  local ints, highSet = self:buildDistributionPoints(mode, targetTotal)
  if ints == nil then
    local ratios
    ratios, highSet = self:buildDistributionRatios(mode, targetTotal)
    ints = {}
    for i = 1, 5 do
      ints[i] = math.floor(targetTotal * ratios[i])
    end
  end
  local minArr, maxArr = self:buildBpBoundsForMode(targetTotal, mode, highSet)
  ints = self:rebalanceBpIntsPerStat(ints, targetTotal, minArr, maxArr)
  return self:applyPerStatCapAndRebalance(ints, targetTotal)
end"""

BOUNDS_MODE1_OLD = """    elseif mode == 1 then
      if isHigh then
        mins[i] = math.max(1, math.floor(targetTotal * SUMMON_BP_A_HIGH_MIN))
        maxs[i] = math.max(mins[i], math.min(cap, math.floor(targetTotal * SUMMON_BP_A_HIGH_MAX)))
      else
        mins[i] = math.max(1, math.floor(targetTotal * SUMMON_BP_FOCUS_LOW_MIN_RATIO_A))
        maxs[i] = math.max(mins[i], math.min(cap, math.floor(targetTotal * 0.22)))
      end"""

BOUNDS_MODE1_NEW = """    elseif mode == 1 then
      if isHigh then
        mins[i] = math.max(1, math.min(cap, SUMMON_BP_SINGLE_HIGH_MIN))
        maxs[i] = cap
      else
        mins[i] = math.max(1, math.floor(targetTotal * SUMMON_BP_FOCUS_LOW_MIN_RATIO))
        maxs[i] = math.max(mins[i], math.min(cap, math.floor(targetTotal * 0.28)))
      end"""


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    for old, new in [
        (CONST_OLD, CONST_NEW),
        (ROLL_TWO_OLD, ""),
        (BUILD_DIST_OLD, BUILD_DIST_NEW),
        (SPLIT_OLD, SPLIT_NEW),
        (BOUNDS_MODE1_OLD, BOUNDS_MODE1_NEW),
    ]:
        if old not in text:
            raise SystemExit(f"missing anchor: {old[:70]!r}")
        text = text.replace(old, new, 1)
    anchor = "function Module:buildDistributionRatios(mode, targetTotal)"
    if "function Module:buildDistributionPoints" not in text:
        text = text.replace(anchor, CAP_AWARE_FUNCS + "\n" + anchor, 1)
    return text


def main() -> int:
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(LOCAL)], check=True)
    fixed = patch(LOCAL.read_bytes().decode("gbk"))
    OUT.write_bytes(fixed.encode("gbk") + b"\n")
    subprocess.run(["scp", str(OUT), f"{REMOTE}:{REMOTE_LUA}"], check=True)
    trigger = Path(r"C:/Users/User/.cursor/skills/cgmsv-restart/scripts/trigger_desktop_restart.ps1")
    subprocess.run(["scp", str(trigger), f"{REMOTE}:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1"], check=True)
    subprocess.run(
        [
            "ssh",
            REMOTE,
            "powershell -NoProfile -ExecutionPolicy Bypass -File C:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1",
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
