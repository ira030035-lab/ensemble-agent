import hmac,hashlib,base64,time,aiohttp,logging
log=logging.getLogger("bitget")
class BitgetClient:
 def __init__(self,cfg):
  self.cfg=cfg;self.base=cfg.BITGET_BASE_URL;self.session=None
 async def start(self):self.session=aiohttp.ClientSession()
 async def close(self):
  if self.session:await self.session.close()
 def _sign(self,ts,method,path,body=""):
  import hmac,hashlib,base64
  msg=f"{ts}{method.upper()}{path}{body}"
  return base64.b64encode(hmac.new(self.cfg.BITGET_SECRET.encode(),msg.encode(),hashlib.sha256).digest()).decode()
 def _headers(self,method,path,body=""):
  import time;ts=str(int(time.time()*1000))
  return {"ACCESS-KEY":self.cfg.BITGET_API_KEY,"ACCESS-SIGN":self._sign(ts,method,path,body),"ACCESS-TIMESTAMP":ts,"ACCESS-PASSPHRASE":self.cfg.BITGET_PASSPHRASE,"Content-Type":"application/json","locale":"en-US"}
 async def get(self,path,params=None):
  async with self.session.get(self.base+path,headers=self._headers("GET",path),params=params) as r:return await r.json()
 async def post(self,path,body):
  import json;bs=json.dumps(body)
  async with self.session.post(self.base+path,headers=self._headers("POST",path,bs),data=bs) as r:return await r.json()
 async def get_top_symbols(self,n=50):
  data=await self.get("/api/v2/mix/market/tickers",{"productType":"USDT-FUTURES"})
  t=sorted(data.get("data",[]),key=lambda x:float(x.get("usdtVolume",0)),reverse=True)
  return [x["symbol"] for x in t[:n]]
 async def get_candles(self,symbol,granularity="15m",limit=100):
  data=await self.get("/api/v2/mix/market/candles",{"symbol":symbol,"productType":"USDT-FUTURES","granularity":granularity,"limit":str(limit)})
  return data.get("data",[])
 async def get_orderbook(self,symbol,limit=20):
  data=await self.get("/api/v2/mix/market/merge-depth",{"symbol":symbol,"productType":"USDT-FUTURES","limit":str(limit)})
  return data.get("data",{})
 async def get_funding_rate(self,symbol):
  data=await self.get("/api/v2/mix/market/current-fund-rate",{"symbol":symbol,"productType":"USDT-FUTURES"})
  try:return float(data["data"][0]["fundingRate"])
  except:return 0.0
 async def get_account_balance(self):
  data=await self.get("/api/v2/mix/account/accounts",{"productType":"USDT-FUTURES"})
  try:return float(data["data"][0]["usdtEquity"])
  except:return 0.0
 async def get_positions(self):
  data=await self.get("/api/v2/mix/position/all-position",{"productType":"USDT-FUTURES"})
  return [p for p in data.get("data",[]) if float(p.get("total",0))>0]
 async def place_order(self,symbol,side,size,leverage=5):
  await self.post("/api/v2/mix/account/set-leverage",{"symbol":symbol,"productType":"USDT-FUTURES","marginCoin":"USDT","leverage":str(leverage),"holdSide":side})
  t=await self.get("/api/v2/mix/market/ticker",{"symbol":symbol,"productType":"USDT-FUTURES"})
  price=float(t["data"][0]["lastPr"]);qty=round(size/price,4)
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":str(qty),"side":"open_long" if side=="long" else "open_short","orderType":"market","tradeSide":"open"})
 async def close_position(self,symbol,side):
  return await self.post("/api/v2/mix/order/place-order",{"symbol":symbol,"productType":"USDT-FUTURES","marginMode":"isolated","marginCoin":"USDT","size":"0","side":"close_long" if side=="long" else "close_short","orderType":"market","tradeSide":"close","reduceOnly":"YES"})
