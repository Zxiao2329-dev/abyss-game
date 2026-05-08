import streamlit as st
import random
import pandas as pd

# --- 1. 游戏配置与初始化 ---
st.set_page_config(page_title="深渊大师：赌狗觉醒", layout="centered")

# 初始化 session_state（Streamlit 存储数据的核心）
if 'game_init' not in st.session_state:
    st.session_state.game_init = False
    st.session_state.player = {}
    st.session_state.logs = ["🎮 欢迎来到深渊！请选择你的命运。"]
    st.session_state.level = 1
    st.session_state.pos = [2, 2] # x, y
    st.session_state.monsters = []
    st.session_state.dodge_rate = 0.3
    st.session_state.gold = 100
    st.session_state.game_over = False

# --- 2. 核心函数 ---
def add_log(msg):
    st.session_state.logs.append(msg)
    if len(st.session_state.logs) > 6:
        st.session_state.logs.pop(0)

def spawn_monsters():
    st.session_state.monsters = []
    for i in range(3):
        m = {
            "pos": [random.randint(4, 13), random.randint(1, 6)],
            "hp": 40 + st.session_state.level * 15,
            "atk": 5 + st.session_state.level * 2,
            "id": i
        }
        st.session_state.monsters.append(m)

def init_player(job_type):
    if job_type == "赌狗":
        # 50% 生死赌局
        if random.random() < 0.5:
            st.session_state.player = {"name": "赌狗", "hp": 15, "max_hp": 15, "atk": 100, "crt": 20, "icon": "🐺"}
            st.session_state.dodge_rate = 0.3
            add_log("✅ 【赌赢了！】获得开局神装，攻击飙升！")
        else:
            st.session_state.game_over = True
            add_log("💀 【赌输了！】你还没进深渊就破产暴毙了。")
    else:
        st.session_state.player = {"name": "战士", "hp": 150, "max_hp": 150, "atk": 25, "crt": 5, "icon": "🤺"}
    
    st.session_state.game_init = True
    spawn_monsters()

def move(dx, dy):
    new_x = st.session_state.pos[0] + dx
    new_y = st.session_state.pos[1] + dy
    
    # 边界检测
    if 0 <= new_x <= 14 and 0 <= new_y <= 7:
        # 碰撞怪兽检测
        hit = False
        for m in st.session_state.monsters:
            if m["pos"] == [new_x, new_y]:
                # 赌狗免伤判定
                if st.session_state.player["name"] == "赌狗" and random.random() < st.session_state.dodge_rate:
                    if st.session_state.dodge_rate < 0.8:
                        st.session_state.dodge_rate += 0.05
                    add_log(f"⚡ 闪避成功！免疫概率升至 {int(st.session_state.dodge_rate*100)}%")
                else:
                    dmg = m["atk"]
                    st.session_state.player["hp"] -= dmg
                    add_log(f"💢 撞怪受伤: -{dmg} HP")
                hit = True
                break
        
        if not hit:
            st.session_state.pos = [new_x, new_y]
    
    if st.session_state.player["hp"] <= 0:
        st.session_state.game_over = True

def attack():
    px, py = st.session_state.pos
    hit_any = False
    for m in st.session_state.monsters[:]:
        if abs(m["pos"][0] - px) <= 1 and abs(m["pos"][1] - py) <= 1:
            dmg = st.session_state.player["atk"]
            if random.random() < (st.session_state.player["crt"]/100):
                dmg *= 2
                add_log("💥 暴击！！")
            m["hp"] -= dmg
            add_log(f"⚔️ 造成 {int(dmg)} 点伤害")
            if m["hp"] <= 0:
                st.session_state.monsters.remove(m)
                st.session_state.gold += 50
                add_log("💀 击杀影子，获得 50G")
            hit_any = True
    
    if not hit_any:
        add_log("💨 打空了...")
    
    if not st.session_state.monsters:
        st.session_state.level += 1
        st.session_state.player["hp"] = min(st.session_state.player["max_hp"], st.session_state.player["hp"] + 20)
        spawn_monsters()
        add_log(f"🎊 进入第 {st.session_state.level} 层！")

# --- 3. 界面渲染 ---
st.title("🎲 深渊大师：Streamlit 觉醒版")

# 还没开始游戏时显示职业选择
if not st.session_state.game_init:
    st.subheader("选择你的开局职业：")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🐺 赌狗 (HP:10 ATK:80)"):
            init_player("赌狗")
            st.rerun()
    with c2:
        if st.button("🤺 战士 (HP:150 ATK:25)"):
            init_player("战士")
            st.rerun()

# 游戏结束界面
elif st.session_state.game_over:
    st.error("💀 游戏结束")
    st.write(f"最终层数: {st.session_state.level}")
    if st.button("重新开始"):
        st.session_state.clear()
        st.rerun()

# 正式游戏界面
else:
    # 侧边栏状态栏
    with st.sidebar:
        st.header("📊 角色状态")
        p = st.session_state.player
        st.metric("生命值 ❤️", f"{int(p['hp'])}/{p['max_hp']}")
        st.metric("基础攻击 ⚔️", p['atk'])
        st.metric("金币 💰", st.session_state.gold)
        if p["name"] == "赌狗":
            st.metric("老道免疫率 🃏", f"{int(st.session_state.dodge_rate*100)}%")
        
        st.divider()
        st.write(f"当前层数: {st.session_state.level}")

    # 主界面：地图显示
    # 用表格或文本阵列渲染地图
    grid = []
    for y in range(8):
        row = []
        for x in range(15):
            char = "⬜"
            if [x, y] == st.session_state.pos:
                char = st.session_state.player["icon"]
            else:
                for m in st.session_state.monsters:
                    if m["pos"] == [x, y]:
                        char = "👾"
            row.append(char)
        grid.append(" ".join(row))
    
    st.code("\n".join(grid)) # 使用代码块保持等宽显示

    # 战斗日志
    with st.expander("📜 查看战斗日志", expanded=True):
        for log in st.session_state.logs[::-1]:
            st.write(log)

    # 底部控制器
    st.divider()
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1,2,1])
    
    with ctrl_col2:
        # 方向键盘
        u1, u2, u3 = st.columns(3)
        with u2: 
            if st.button("🔼"): move(0, -1); st.rerun()
        
        l1, l2, l3 = st.columns(3)
        with l1: 
            if st.button("◀️"): move(-1, 0); st.rerun()
        with l2:
            if st.button("⚔️ 攻击"): attack(); st.rerun()
        with l3:
            if st.button("▶️"): move(1, 0); st.rerun()
            
        d1, d2, d3 = st.columns(3)
        with d2:
            if st.button("🔽"): move(0, 1); st.rerun()

