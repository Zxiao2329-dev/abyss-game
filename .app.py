import streamlit as st
import random
import re

# --- 1. 基础配置数据 ---
ELEMENTS = {"🔥火": "🍃草", "🍃草": "💧水", "💧水": "🔥火"}
JOBS = {
    "1": {"name": "战士", "hp": 150, "atk": 15, "icon": "🤺", "elem": "🔥火"},
    "2": {"name": "刺客", "hp": 100, "atk": 25, "icon": "🥷", "elem": "💧水"},
    "3": {"name": "法师", "hp": 80, "atk": 20, "icon": "🧙", "elem": "🍃草"}
}
PETS_INIT = [("小火龙","🔥火","🦖"), ("杰尼龟","💧水","🐢"), ("妙蛙草","🍃草","🐸")]

# --- 2. 初始化 Session State (修复报错的核心) ---
# 确保所有变量在页面加载时就有初始值，防止 append 报错
if 'game_init' not in st.session_state:
    st.session_state.game_init = False
    st.session_state.is_over = False
    st.session_state.logs = ["📢 欢迎来到深渊！"]
    st.session_state.level = 1
    st.session_state.gold = 100
    st.session_state.pos = [2, 2]
    st.session_state.player = {}
    st.session_state.monsters = []  # 初始化怪物列表
    st.session_state.items = []     # 初始化道具列表
    st.session_state.pets = []      # 初始化宠物列表
    st.session_state.active_pet_idx = 0

def add_log(msg):
    st.session_state.logs.append(msg)
    if len(st.session_state.logs) > 8: st.session_state.logs.pop(0)

def calc_dmg(atk_elem, def_elem, base):
    if ELEMENTS.get(atk_elem) == def_elem:
        return int(base * 1.5), " (克制↑)"
    elif ELEMENTS.get(def_elem) == atk_elem:
        return int(base * 0.7), " (被克制↓)"
    return base, ""

def spawn_world():
    level = st.session_state.level
    st.session_state.monsters = []
    st.session_state.items = [] # 每次生成世界前确保清空并重新设为列表
    
    # 生成怪物
    if level % 5 == 0:
        st.session_state.monsters.append({
            "pos": [13, 4], "name": "👹深渊领主", "elem": random.choice(list(ELEMENTS.keys())),
            "hp": 200 + level*20, "max_hp": 200 + level*20, "atk": 15 + level*3, "is_boss": True
        })
        add_log("📢 警告：强大的 BOSS 挡住了去路！")
    else:
        for _ in range(2 + level % 5):
            e = random.choice(list(ELEMENTS.keys()))
            st.session_state.monsters.append({
                "pos": [random.randint(5, 13), random.randint(1, 6)],
                "name": f"{e}灵", "elem": e, "hp": 40 + level*8, "max_hp": 40 + level*8, "atk": 5 + level, "is_boss": False
            })
    # 生成金币
    st.session_state.items.append({"pos": [random.randint(2, 13), random.randint(1, 6)], "type": "💰"})

# --- 3. 游戏核心逻辑 ---
def move(dire, steps=1):
    old_pos = list(st.session_state.pos)
    for _ in range(steps):
        nx, ny = st.session_state.pos
        if dire == 'w': ny -= 1
        elif dire == 's': ny += 1
        elif dire == 'a': nx -= 1
        elif dire == 'd': nx += 1
        
        if 1 <= nx <= 13 and 1 <= ny <= 6:
            st.session_state.pos = [nx, ny]
        else: break
        
    # 拾取金币
    for i in st.session_state.items[:]:
        if i["pos"] == st.session_state.pos:
            st.session_state.gold += 50
            add_log("💰 获得金币 +50")
            st.session_state.items.remove(i)
            
    # 怪物碰撞
    for m in st.session_state.monsters:
        if m["pos"] == st.session_state.pos:
            st.session_state.player["cur_hp"] -= m["atk"]
            st.session_state.pos = old_pos
            add_log(f"💥 被{m['name']}撞击，损失 {m['atk']} HP")
            
    if st.session_state.player["cur_hp"] <= 0:
        st.session_state.is_over = True

def do_attack():
    p = st.session_state.player
    active_pet = st.session_state.pets[st.session_state.active_pet_idx]
    px, py = st.session_state.pos
    hit = False
    
    for m in st.session_state.monsters[:]:
        if abs(m["pos"][0]-px) <= 1 and abs(m["pos"][1]-py) <= 1:
            p_dmg, p_txt = calc_dmg(p["elem"], m["elem"], p["atk"])
            pt_dmg, pt_txt = calc_dmg(active_pet["elem"], m["elem"], active_pet["atk"])
            total = p_dmg + pt_dmg
            m["hp"] -= total
            add_log(f"⚔️ 总计造成{total}伤害{p_txt}{pt_txt}")
            if m["hp"] <= 0:
                st.session_state.monsters.remove(m)
                st.session_state.gold += 30
                add_log(f"💀 击败了{m['name']}")
            hit = True
    
    if not hit: add_log("💨 打空了...")
    
    # 检查是否通关进入下一层
    if not st.session_state.monsters:
        st.session_state.level += 1
        st.session_state.player["cur_hp"] = min(st.session_state.player["cur_hp"]+20, st.session_state.player["hp"])
        spawn_world()
        add_log(f"🎊 成功通关！进入第{st.session_state.level}层")

def do_capture():
    px, py = st.session_state.pos
    for m in st.session_state.monsters[:]:
        if abs(m["pos"][0]-px) <= 1 and abs(m["pos"][1]-py) <= 1:
            if m["hp"] < m["max_hp"] * 0.5 and random.random() < 0.65:
                new_pet = {"name": m["name"], "elem": m["elem"], "icon": "🐾", "atk": 10 + st.session_state.level}
                st.session_state.pets.append(new_pet)
                st.session_state.monsters.remove(m)
                add_log(f"💖 成功收服了{m['name']}！")
            else:
                add_log("💢 怪物挣扎着逃脱了...")
            return
    add_log("❓ 附近没有可以捕捉的怪物")

# --- 4. 界面渲染 ---
st.set_page_config(page_title="深渊大师", layout="centered")
st.title("🛡️ 深渊大师：宠物之门")

if not st.session_state.game_init:
    st.subheader("选择你的初始配置")
    c1, c2 = st.columns(2)
    job_sel = c1.selectbox("职业", ["战士 (🔥)", "刺客 (💧)", "法师 (🍃)"])
    pet_sel = c2.selectbox("初始宠物", ["小火龙 (🔥)", "杰尼龟 (💧)", "妙蛙草 (🍃)"])
    
    if st.button("开启深渊之旅", use_container_width=True):
        # 初始化玩家
        j_idx = ["战士 (🔥)", "刺客 (💧)", "法师 (🍃)"].index(job_sel)
        st.session_state.player = JOBS[str(j_idx+1)].copy()
        st.session_state.player["cur_hp"] = st.session_state.player["hp"]
        
        # 初始化首个宠物
        p_idx = ["小火龙 (🔥)", "杰尼龟 (💧)", "妙蛙草 (🍃)"].index(pet_sel)
        p_data = PETS_INIT[p_idx]
        st.session_state.pets = [{"name": p_data[0], "elem": p_data[1], "icon": p_data[2], "atk": 10}]
        
        st.session_state.game_init = True
        spawn_world()
        st.rerun()

elif st.session_state.is_over:
    st.error("💀 你英勇地牺牲在深渊中...")
    if st.button("转世重修"):
        # 完全重置 Session State
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

else:
    # 侧边栏状态栏
    with st.sidebar:
        p = st.session_state.player
        st.header(f"{p['icon']} {p['name']}")
        st.progress(max(0.0, p['cur_hp']/p['hp']), text=f"HP: {p['cur_hp']}/{p['hp']}")
        st.write(f"⚔️ 攻击: {p['atk']} | 💰 金币: {st.session_state.gold}")
        st.divider()
        st.write(f"🐾 当前出战: {st.session_state.pets[st.session_state.active_pet_idx]['name']}")
        
        with st.expander("🐶 宠物仓库", expanded=True):
            for i, pt in enumerate(st.session_state.pets):
                if st.button(f"{pt['icon']} {pt['name']} (ATK:{pt['atk']})", key=f"p_{i}"):
                    st.session_state.active_pet_idx = i
                    add_log(f"🐾 切换出战: {pt['name']}")
                    st.rerun()
        
        st.divider()
        if st.button("🏠 重置游戏 (退出当前存档)"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # 地图区域
    grid = []
    for y in range(8):
        row = []
        for x in range(15):
            char = "⬜"
            if x == 0 or x == 14 or y == 0 or y == 7: char = "🧱"
            elif [x, y] == st.session_state.pos: char = p["icon"]
            else:
                # 检查怪物
                found_entity = False
                for m in st.session_state.monsters:
                    if m["pos"] == [x, y]: 
                        char = "👹" if m.get("is_boss") else "👾"
                        found_entity = True
                        break
                # 检查金币
                if not found_entity:
                    for i in st.session_state.items:
                        if i["pos"] == [x, y]: 
                            char = i["type"]
                            break
            row.append(char)
        grid.append(" ".join(row))
    
    st.code("\n".join(grid))

    # 底部控制盘
    col_move, col_act = st.columns([2, 1])
    with col_move:
        m1, m2, m3 = st.columns(3)
        if m2.button("🔼"): move('w'); st.rerun()
        m4, m5, m6 = st.columns(3)
        if m4.button("◀️"): move('a'); st.rerun()
        if m5.button("🔄"): st.rerun()
        if m6.button("▶️"): move('d'); st.rerun()
        m7, m8, m9 = st.columns(3)
        if m8.button("🔽"): move('s'); st.rerun()

    with col_act:
        if st.button("⚔️ 攻击", use_container_width=True): do_attack(); st.rerun()
        if st.button("💖 捕捉", use_container_width=True): do_capture(); st.rerun()

    # 日志
    with st.expander("📜 冒险日志", expanded=True):
        for log in st.session_state.logs[::-1]: st.write(log)
# --- 找到 move 函数，在里面添加安全判定 ---
def move(dire, steps=1):
    # 保险 1：如果 items 消失了，立刻补上
    if "items" not in st.session_state or st.session_state.items is None:
        st.session_state.items = []
        
    old_pos = list(st.session_state.pos)
    for _ in range(steps):
        nx, ny = st.session_state.pos
        if dire == 'w': ny -= 1
        elif dire == 's': ny += 1
        elif dire == 'a': nx -= 1
        elif dire == 'd': nx += 1
        
        if 1 <= nx <= 13 and 1 <= ny <= 6:
            st.session_state.pos = [nx, ny]
        else: break
        
    # 拾取逻辑
    for i in st.session_state.items[:]:
        if i["pos"] == st.session_state.pos:
            st.session_state.gold += 50
            add_log("💰 获得金币 +50")
            st.session_state.items.remove(i)
