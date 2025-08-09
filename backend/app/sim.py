import pandas as pd, numpy as np
from datetime import datetime
try:
    from pycoingecko import CoinGeckoAPI
    cg = CoinGeckoAPI()
    USING_CG = True
except Exception:
    USING_CG = False
try:
    import lightgbm as lgb
    MODEL='lgb'
except Exception:
    from sklearn.ensemble import RandomForestClassifier
    MODEL='rf'
from sklearn.ensemble import RandomForestClassifier

def fetch_price(ticker, start, end):
    if USING_CG:
        coin_map = {ticker.upper(): ticker.lower()}
        # use coin id search
        try:
            coins = cg.get_coins_list()
            match = next((c for c in coins if c['symbol'].lower()==ticker.lower() or c['id']==ticker.lower()), None)
            cid = match['id'] if match else ticker.lower()
        except Exception:
            cid = ticker.lower()
        data = cg.get_coin_market_chart_by_id(cid, vs_currency='gbp', days='max')
        df = pd.DataFrame(data['prices'], columns=['ts','price'])
        df['date'] = pd.to_datetime(df['ts'], unit='ms')
        df = df.set_index('date')
        s = df['price'].resample('D').mean().ffill()
        return s[start:end]
    else:
        import yfinance as yf
        sym = ticker + '-USD' if '-' not in ticker else ticker
        df = yf.download(sym, start=start, end=end, progress=False)['Adj Close']
        return df

def features(series):
    df = pd.DataFrame({'close': series})
    df['r1'] = df['close'].pct_change(1)
    df['r7'] = df['close'].pct_change(7)
    df['r30'] = df['close'].pct_change(30)
    df['s7'] = df['close'].rolling(7).mean()
    df['s30'] = df['close'].rolling(30).mean()
    df['v14'] = df['r1'].rolling(14).std()
    df = df.dropna()
    df['target'] = (df['close'].shift(-30)/df['close'] -1) > 0
    return df

def train_model(series):
    df = features(series)
    if len(df) < 150:
        return None, None
    X = df.drop(columns=['close','target'])
    y = df['target'].astype(int)
    if MODEL=='lgb':
        import lightgbm as lgb
        ltrain = lgb.Dataset(X, label=y)
        params = {'objective':'binary','verbose':-1}
        clf = lgb.train(params, ltrain, num_boost_round=100)
        return clf, list(X.columns)
    else:
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X,y)
        return clf, list(X.columns)

def run_simulation(tickers, monthly=50.0, start='2019-01-01', end=None):
    if end is None:
        end = datetime.utcnow().strftime('%Y-%m-%d')
    price_map = {}
    for t in tickers:
        s = fetch_price(t, start, end)
        price_map[t] = s
    prices = pd.concat(price_map, axis=1)
    prices.columns = tickers
    prices = prices.ffill().dropna(how='all')
    models = {}
    for t in tickers:
        ser = prices[t].dropna()
        clf, cols = train_model(ser)
        if clf is not None:
            models[t] = (clf, cols)
    dates = prices.index
    months = sorted(list({(d.year,d.month) for d in dates}))
    holdings_bh = {t:0.0 for t in tickers}
    holdings_ai = {t:0.0 for t in tickers}
    cash_bh = 0.0; cash_ai = 0.0
    history = []
    for y,m in months:
        d = [dt for dt in dates if dt.year==y and dt.month==m][0]
        cash_bh += monthly; cash_ai += monthly
        alloc = monthly/len(tickers)
        for t in tickers:
            price = prices.at[d,t]
            qty = alloc/price
            holdings_bh[t] += qty; cash_bh -= alloc
            buy = True
            if t in models:
                clf, cols = models[t]
                win = prices[t].loc[:d]
                feat = features(win).iloc[-1:][cols]
                if MODEL=='lgb':
                    pred = clf.predict(feat)[0]
                else:
                    pred = clf.predict(feat)[0]
                buy = bool(pred)
            if buy:
                qty2 = alloc/price
                holdings_ai[t] += qty2; cash_ai -= alloc
        total_bh = cash_bh + sum(holdings_bh[t]*prices.at[d,t] for t in tickers)
        total_ai = cash_ai + sum(holdings_ai[t]*prices.at[d,t] for t in tickers)
        history.append({'date': d, 'bh': total_bh, 'ai': total_ai})
    hist = pd.DataFrame(history).set_index('date')
    def stats(series):
        rtn = series.pct_change().dropna()
        years = (series.index[-1]-series.index[0]).days/365.25
        cagr = (series.iloc[-1]/series.iloc[0])**(1/years)-1 if years>0 else None
        vol = rtn.std()* (252**0.5)
        mdd = (series/series.cummax()-1).min()
        return {'CAGR': cagr, 'Vol': vol, 'MaxDD': mdd}
    return {'history': hist.reset_index().to_dict(orient='records'), 'bh_stats': stats(hist['bh']), 'ai_stats': stats(hist['ai'])}
