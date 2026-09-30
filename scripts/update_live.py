import json, urllib.request

URL="https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load"
req=urllib.request.Request(URL,headers={"Accept":"application/json","User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req,timeout=60) as r:
    payload=json.load(r)

rows=((payload.get("waterlevel_data") or {}).get("data") or [])
labels={1:"ปกติ",2:"เฝ้าระวัง",3:"น้ำมาก",4:"เสี่ยงสูง",5:"วิกฤต"}

def lang(obj,key):
    v=(obj or {}).get(key)
    if isinstance(v,dict):
        return v.get("th") or v.get("en") or ""
    return v or ""

def level(row):
    if str(row.get("diff_wl_bank_text") or "").startswith("ล้นตลิ่ง"):
        return 5
    try:return int(row.get("situation_level") or 0)
    except:return 0

provinces={}
latest=""
for row in rows:
    p=lang(row.get("geocode") or {},"province_name")
    if not p: continue
    lv=level(row)
    dt=str(row.get("waterlevel_datetime") or "")
    latest=max(latest,dt)
    st=row.get("station") or {}
    rec={"province":p,"state":labels.get(lv,"ยังไม่มีข้อมูลตรง"),"situation_level":lv,
         "station_name":lang(st,"tele_station_name"),"station_code":st.get("tele_station_oldcode") or "",
         "waterlevel_msl":row.get("waterlevel_msl"),"waterlevel_m":row.get("waterlevel_m"),
         "discharge":row.get("discharge"),"datetime":dt,"diff_wl_bank":row.get("diff_wl_bank"),
         "diff_wl_bank_text":row.get("diff_wl_bank_text") or ""}
    old=provinces.get(p)
    if old is None or lv>old["situation_level"] or (lv==old["situation_level"] and dt>old["datetime"]):
        provinces[p]=rec

out={"source":"ThaiWater / National Hydroinformatics Data Center","source_url":URL,
     "source_updated_at":latest,"province_count":len(provinces),"station_count":len(rows),"provinces":provinces}
with open("live-water.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,separators=(",",":"))
