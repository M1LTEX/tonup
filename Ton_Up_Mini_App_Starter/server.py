import sqlite3, random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DB=Path(__file__).with_name("tonup.db")
app=FastAPI(title="Ton Up API")
ITEMS={"Мішка":15,"Кубок":40,"Подарунок":25,"Колечко":100,"Шампанське":50,"Морозиво NFT (демо)":120,"Колекційний NFT (демо)":180}

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    with db() as c:
        c.execute("CREATE TABLE IF NOT EXISTS users(user_id TEXT PRIMARY KEY, coins INTEGER NOT NULL DEFAULT 100, inventory TEXT NOT NULL DEFAULT '')")
        c.execute("CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, user_id TEXT, action TEXT, amount INTEGER, result TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
init()
def user(uid):
    with db() as c:
        c.execute("INSERT OR IGNORE INTO users(user_id,coins,inventory) VALUES (?,100,'')",(uid,))
        return dict(c.execute("SELECT * FROM users WHERE user_id=?",(uid,)).fetchone())
def save(uid,coins,inv):
    with db() as c: c.execute("UPDATE users SET coins=?,inventory=? WHERE user_id=?",(coins,",".join(inv),uid))
def log(uid,action,amount,result):
    with db() as c: c.execute("INSERT INTO history(user_id,action,amount,result) VALUES (?,?,?,?)",(uid,action,amount,result))

class Play(BaseModel):
    user_id:str=Field(min_length=1,max_length=80)
    game:str
    amount:int=Field(default=1,ge=1,le=10000)
    case_id:int=1
    item:str=""
class Sell(BaseModel):
    user_id:str
    item:str

@app.get("/api/profile/{uid}")
def profile(uid):
    u=user(uid)
    return {"user_id":uid,"coins":u["coins"],"inventory":[x for x in u["inventory"].split(",") if x],"items":ITEMS}

@app.post("/api/play")
def play(r:Play):
    u=user(r.user_id); coins=u["coins"]; inv=[x for x in u["inventory"].split(",") if x]
    if r.game=="plinko": cost=1
    elif r.game=="case":
        cost={1:15,2:25,3:50}.get(r.case_id)
        if cost is None: raise HTTPException(400,"Невідомий кейс")
    elif r.game in ("upgrade","cow"): cost=r.amount
    else: raise HTTPException(400,"Невідома гра")
    if r.game=="upgrade" and r.item not in ITEMS: raise HTTPException(400,"Невідомий предмет")
    if coins<cost: raise HTTPException(400,"Недостатньо тестових монет")
    coins-=cost; prize=None
    if r.game=="case":
        options={1:(["Мішка","Кубок"],[75,25]),2:(["Подарунок","Колечко"],[75,25]),3:(["Шампанське","Колечко"],[75,25])}
        prize=random.choices(*options[r.case_id])[0]; inv.append(prize); result="Випало: "+prize
    elif r.game=="plinko":
        mult=random.choice([0,0,0,2,3,5]); win=cost*mult; coins+=win; result=f"Множник x{mult}; результат +{win} монет"
    elif r.game=="upgrade":
        if random.random()<0.35: inv.append(r.item); result="Апгрейд успішний: "+r.item
        else: result="Апгрейд не вдався"
    else:
        risk={"low":.20,"medium":.40,"high":.65}.get(r.item,.20)
        if random.random()<risk: result="Коровка з'їла виграш 😅"
        else:
            win=int(cost*{"low":1.5,"medium":2.5,"high":4}.get(r.item,1.5)); coins+=win
            result=f"Успіх! Повернення {win} тестових монет"
    save(r.user_id,coins,inv); log(r.user_id,r.game,cost,result)
    return {"coins":coins,"inventory":inv,"result":result,"prize":prize}

@app.post("/api/sell")
def sell(r:Sell):
    u=user(r.user_id); inv=[x for x in u["inventory"].split(",") if x]
    if r.item not in inv: raise HTTPException(400,"Предмета немає в інвентарі")
    inv.remove(r.item); value=max(1,ITEMS.get(r.item,10)//2); coins=u["coins"]+value
    save(r.user_id,coins,inv); log(r.user_id,"sell",value,r.item)
    return {"coins":coins,"inventory":inv,"result":f"Продано за {value} монет"}

@app.get("/api/health")
def health(): return {"ok":True,"app":"Ton Up"}
app.mount("/",StaticFiles(directory=Path(__file__).with_name("web"),html=True),name="web")
