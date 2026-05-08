import streamlit as st
import random

# --- 1. 初始化 (新增能量系统 mp) ---
if 'init' not in st.session_state:
    st.session_state.init = False
    st.session_state.player = {}
    st.session_state.logs = ["📢 欢迎来到《深渊大师：技能觉醒》！"]
    st.session_state.level = 1
    st.session_state.pos = [2, 2]
    st.session_state.monsters = []
    st.session_state.gold = 100
    st.session_state.is_over = False

def add_log(msg):
    st.session_state.logs.append(msg)
    if len(st.session_state.logs) > 8: st.session_state.logs.pop(0)

# --- 2. 大招逻辑 (核心玩法) ---
def cast_ultimate():
    p = st.session_state.player
    if p["mp"] < 100:
        add_log("❌ 能量不足！需要 100 点能量（杀怪或移动可回复）。")
        return

    if p["job"] == "赌狗":
        # 大招：梭哈之王
        add_log("🃏 【梭哈！】你赌上了全部身家！")
        if random.random() < 0.4:
            p["atk"] *= 3
            add_log("🔥 豪赌成功！本层攻击力翻 3 倍！！")
        else:
            p["hp"] = 1
            add_log("💸 赌崩了！生命值降为 1 点，但这才是真正的赌徒！")
            
    elif p["job"] == "战士":
        # 大招：旋风斩
        add_log("🌪️ 【旋风斩！】对周围所有敌人造成毁灭打击！")
        for m in st.session_state.monsters[:]:
            dist = abs(m["pos"][0]-st.session_state.pos[0]) + abs(m["pos"][1]-st.session_state.pos[1])
            if dist <= 3:
                m["hp"] -= p["atk"] * 2
                if m["hp"] <= 0: st.session_state.monsters.remove(m)
        add_log("⚔️ 周围的影子被肃清了。")

    elif p["job"] == "嘉豪":
        # 大招：复制粘贴
        add_log("🎭 【复制粘贴！】嘉豪偷取了深渊的力量。")
        p["hp"] = p["max_hp"] # 直接满血
        p["atk"] += 20
        add_log("✨ 状态全满，且攻击力永久永久提升 20！")

    p["mp"] = 0 # 释放后清空能量

# --- 3. 基础逻辑 (带能量回复) ---
def move(dx, dy):
    nx, ny = st.session_state.pos[0] + dx, st.session_state.pos[1] + dy
    if 0 <= nx <= 14 and 0 <= ny <= 7:
        for m in st.session_state.monsters:
            if m["pos"] == [nx, ny]:
                if random.random() < st.session_state.player["dodge"]:
                    add_log("✨ 闪避成功！")
                else:
                    dmg = m["atk"]
                    st.session_state.player["hp"] -= dmg
                    add_log(f"💥 撞怪受伤 -{dmg}")
                return
        st.session_state.pos = [nx, ny]
        st.session_state.player["mp"] = min(100, st.session_state.player["mp"] + 5) # 移动回蓝

def fight():
    px, py = st.session_state.pos
    target = None
    for m in st.session_state.monsters:
        if abs(m["pos"][0]-px) <= 1 and abs(m["pos"][1]-py) <= 1:
            target = m; break
    
    if target:
        dmg = st.session_state.player["atk"]
        if random.random() < st.session_state.player["crt"]/100:
            dmg *= 2; add_log("🔥 暴击！")
        target["hp"] -= dmg
        add_log(f"⚔️ 造成 {int(dmg)} 伤害")
        if target["hp"] <= 0:
            st.session_state.monsters.remove(target)
            st.session_state.player["mp"] = min(100, st.session_state.player["mp"] + 30) # 杀怪大幅回蓝
            st.session_state.gold += 50
    
    if not st.session_state.monsters:
        st.session_state.level += 1
        spawn_world()

def spawn_world():
    st.session_state.monsters = []
    for _ in range(3 + st.session_state.level):
        st.session_state.monsters.append({
            "pos": [random.randint(2, 12), random.randint(1, 6)],
            "hp": 50 + st.session_state.level * 20,
            "atk": 10 + st.session_state.level * 5,
            "type": "👾"
        })

def start_game(job):
    if job == "赌狗":
        st.session_state.player = {"job": "赌狗", "hp": 100, "max_hp": 100, "atk": 60, "crt": 30, "icon": "🐺", "dodge": 0.2, "mp": 0}
    elif job == "战士":
        st.session_state.player = {"job": "战士", "hp": 200, "max_hp": 200, "atk": 40, "crt": 10, "icon": "🤺", "dodge": 0.05, "mp": 0}
    elif job == "嘉豪":
        st.session_state.player = {"job": "嘉豪", "hp": 120, "max_hp": 120, "atk": 50, "crt": 20, "icon": "🎭", "dodge": 0.1, "mp": 0}
    st.session_state.init = True
    spawn_world()

# --- 4. 界面渲染 ---
st.title("🛡️ 深渊大师：大招觉醒版")

if not st.session_state.init:
    cols = st.columns(3)
    if cols[0].button("🐺 赌狗"): start_game("赌狗"); st.rerun()
    if cols[1].button("🤺 战士"): start_game("战士"); st.rerun()
    if cols[2].button("🎭 嘉豪"): start_game("嘉豪"); st.rerun()

elif st.session_state.is_over or st.session_state.player["hp"] <= 0:
    st.error("💀 你倒在了深渊里...")
    if st.button("转世重修"): st.session_state.clear(); st.rerun()

else:
    with st.sidebar:
        p = st.session_state.player
        st.header(f"{p['icon']} {p['job']}")
        st.progress(max(0, p['hp']/p['max_hp']), text=f"HP: {int(p['hp'])}")
        st.progress(p['mp']/100, text=f"能量 (MP): {p['mp']}%")
        st.write(f"⚔️ 攻击: {p['atk']} | 💰 金币: {st.session_state.gold}")
        st.divider()
        if st.button("🔥 释放大招", use_container_width=True): cast_ultimate(); st.rerun()

    # 地图和操作
    map_str = []
    for y in range(8):
        row = []
        for x in range(15):
            char = "⬜"
            if [x, y] == st.session_state.pos: char = p["icon"]
            else:
                for m in st.session_state.monsters:
                    if m["pos"] == [x, y]: char = "👾"
            row.append(char)
        map_str.append(" ".join(row))
    st.code("\n".join(map_str))

    # 操作键
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        b = st.columns(3)
        if b[1].button("🔼"): move(0, -1); st.rerun()
        b2 = st.columns(3)
        if b2[0].button("◀️"): move(-1, 0); st.rerun()
        if b2[1].button("⚔️"): fight(); st.rerun()
        if b2[2].button("▶️"): move(1, 0); st.rerun()
        b3 = st.columns(3)
        if b3[1].button("🔽"): move(0, 1); st.rerun()

    with st.expander("📜 战斗记录", expanded=True):
        for l in st.session_state.logs[::-1]: st.write(l)
