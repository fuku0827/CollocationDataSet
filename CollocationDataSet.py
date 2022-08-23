import os
import glob
import stanza
import Stanza_WordPair_Extract
import re
import pandas as pd
import collections
import numpy as np
import datetime

#ジャンル名を入れたリストを作成-----------------------------------------------
os.chdir("C:/Users/wpoto/research/thesis/program/BNC_parse/Parsed_file/Parsed_file")
all_files = glob.glob("*.bin")
genre_names = []
for file_name in all_files:
    genre_names.append(re.sub("_[A-Z0-9][A-Z0-9][A-Z0-9].bin","", file_name))
genre_names = list(set(genre_names))
#----------------------------------------------------------------------------


#変数の初期化-----------------------------------------------------------------
#ジャンルごとに語数を格納する辞書をを初期化
genre_token_dict = {} 

#後で語の頻度を集計するための辞書を初期化
Word_freq = {}

#統語構造内での構成単語の頻度を入れるためのリストを初期化
w1_freq_in_obj = []
w2_freq_in_obj = []
w1_freq_in_amod = []
w2_freq_in_amod = []
w1_freq_in_nounmod = []
w2_freq_in_nounmod = []
w1_freq_in_advmod_verb = []
w2_freq_in_advmod_verb = []
w1_freq_in_advmod_adj = []
w2_freq_in_advmod_adj = []

#wordpairデータを追加していく、データフレームを初期化
df_obj_all = pd.DataFrame()
df_amod_all = pd.DataFrame()
df_nounmod_all = pd.DataFrame()
df_advmod_verb_all = pd.DataFrame()
df_advmod_adj_all = pd.DataFrame()
#----------------------------------------------------------------------------


#ジャンルごとのループ処理------------------------------------------------------------------------------------------------------------------------------
# - ジャンルごとにファイルを読み込む(あとでDPを産出するためにジャンル別頻度を産出するために、ジャンルごと処理をする)
# - 統語構造別にWord pairを抽出
# - 各Word pairの共起頻度を各ジャンルごとに集計するデータフレームを作成する
for cnt, genre_name in enumerate(genre_names):
    print(cnt, datetime.datetime.now(), genre_name, "processing ...")
    files = glob.glob(f"{genre_name}*.bin")  #現在処理中のジャンル名を含むファイル名をリストに格納

    genre_token = 0 #現在処理中のジャンルの総語数を格納する変数を用意

    #各統語構造のWord pairを格納するリストを初期化
    obj_list = []
    amod_list = []
    nounmod_list = []
    advmod_verb_list = []
    advmod_adj_list = []


    #ここから現在処理中のジャンル内の個別ファイルごとにループ処理-----------------------------------------------------------
    for file in files:  #ファイルを読み込み
        with open(file, 'rb') as f:
            doc = f.read()
        doc = stanza.Document.from_serialized(doc)  #構文解析済みバイナリデータをstanzaオブジェクトに復元
        genre_token += doc.num_tokens #現在のファイルの語数を加算
        
        #全単語の頻度を集計
        for word in doc.iter_words():
            if word.lemma in Word_freq.keys():
                Word_freq[word.lemma] += 1
            else:
                Word_freq[word.lemma] = 1
        
        #統語構造別にwordpairを抽出しリストに格納
        obj_pairs = Stanza_WordPair_Extract.obj(doc)
        obj_list.extend(obj_pairs)
        amod_pairs = Stanza_WordPair_Extract.amod(doc)
        amod_list.extend(amod_pairs)
        nounmod_pairs = Stanza_WordPair_Extract.nounmod(doc)
        nounmod_list.extend(nounmod_pairs)
        advmod_verb_pairs = Stanza_WordPair_Extract.advmod_verb(doc)
        advmod_verb_list.extend(advmod_verb_pairs)
        advmod_adj_pairs = Stanza_WordPair_Extract.advmod_adj(doc)
        advmod_adj_list.extend(advmod_adj_pairs)

        #統語構造別に語をリストに格納
        for w1, w2 in obj_pairs:
            w1_freq_in_obj.append(w1)
            w2_freq_in_obj.append(w2)
        for w1, w2 in amod_pairs:
            w1_freq_in_amod.append(w1)
            w2_freq_in_amod.append(w2)
        for w1, w2 in nounmod_pairs:
            w1_freq_in_nounmod.append(w1)
            w2_freq_in_nounmod.append(w2)
        for w1, w2 in advmod_verb_pairs:
            w1_freq_in_advmod_verb.append(w1)
            w2_freq_in_advmod_verb.append(w2)
        for w1, w2 in advmod_adj_pairs:
            w1_freq_in_advmod_adj.append(w1)
            w2_freq_in_advmod_adj.append(w2)
    #ファイルごとのループ処理終了------------------------------------------------------------------------------------------------


    #word pairの頻度を集計しpandasシリーズにまとめる
    obj_Series = pd.Series(collections.Counter(obj_list), name=genre_name)
    amod_Series = pd.Series(collections.Counter(amod_list), name=genre_name)
    nounmod_Series = pd.Series(collections.Counter(nounmod_list), name=genre_name)
    advmod_verb_Series = pd.Series(collections.Counter(advmod_verb_list), name=genre_name)
    advmod_adj_Series = pd.Series(collections.Counter(advmod_adj_list), name=genre_name)

    #上で作成したジャンルごとのwordpairの頻度データを全体のデータフレームに追加
    df_obj_all = pd.concat([df_obj_all, obj_Series], axis=1)
    df_amod_all = pd.concat([df_amod_all, amod_Series], axis=1)
    df_nounmod_all = pd.concat([df_nounmod_all, nounmod_Series], axis=1)
    df_advmod_verb_all = pd.concat([df_advmod_verb_all, advmod_verb_Series], axis=1)
    df_advmod_adj_all = pd.concat([df_advmod_adj_all, advmod_adj_Series], axis=1)

    genre_token_dict[genre_name] = genre_token  #現在処理中のジャンルの総語数を格納

    print('finish')
#ジャンルごとのループ処理終了--------------------------------------------------------------------------------------------------------------------------

print('Processing ... ')
#ジャンルごとの総語数が入ったシリーズを作成
genre_token_Series = pd.Series(genre_token_dict)

#欠損値を0で埋める
df_obj_all.fillna(0, inplace=True)
df_amod_all.fillna(0, inplace=True)
df_nounmod_all.fillna(0, inplace=True)
df_advmod_verb_all.fillna(0, inplace=True)
df_advmod_adj_all.fillna(0, inplace=True)

#DPを算出する関数--------------------------------------------------------------
def DP_calculator(df):
    genre_token_rel = genre_token_Series.values / genre_token_Series.sum()  #各ジャンルが総語数に占める割合を出す
    DP_list = []
    for i in range(len(df)):  #行ごとに処理
        row_values = df.iloc[i].values  #行の値を取得
        row_values_rel = row_values/row_values.sum()  #全体の共起頻度に示る各ジャンル内での頻度の割合を出す
        DP = abs(genre_token_rel - row_values_rel).sum()/2  #DPの算出
        DP_list.append(DP)
    return DP_list  #DPの値を入れたリストを返す
#------------------------------------------------------------------------------


#各フレームのDPを算出
DP_obj = DP_calculator(df_obj_all)
DP_amod = DP_calculator(df_amod_all)
DP_nounmod = DP_calculator(df_nounmod_all)
DP_advmod_verb = DP_calculator(df_advmod_verb_all)
DP_advmod_adj = DP_calculator(df_advmod_adj_all)


#インデックス列を通常の列に変更して列名を付ける
df_obj_all.reset_index(inplace=True)
df_obj_all.rename(columns={'level_0':'w1', 'level_1':'w2'}, inplace=True)
df_amod_all.reset_index(inplace=True)
df_amod_all.rename(columns={'level_0':'w1', 'level_1':'w2'}, inplace=True)
df_nounmod_all.reset_index(inplace=True)
df_nounmod_all.rename(columns={'level_0':'w1', 'level_1':'w2'}, inplace=True)
df_advmod_verb_all.reset_index(inplace=True)
df_advmod_verb_all.rename(columns={'level_0':'w1', 'level_1':'w2'}, inplace=True)
df_advmod_adj_all.reset_index(inplace=True)
df_advmod_adj_all.rename(columns={'level_0':'w1', 'level_1':'w2'}, inplace=True)


#relation(統語パターン)の列を追加
df_obj_all.insert(loc=2, column='relation', value='obj')
df_amod_all.insert(loc=2, column='relation', value='amod')
df_nounmod_all.insert(loc=2, column='relation', value='nounmod')
df_advmod_verb_all.insert(loc=2, column='relation', value='advmod_verb')
df_advmod_adj_all.insert(loc=2, column='relation', value='advmod_adj')


#共起頻度の合計を集計した列(cooccurrence)を追加
df_obj_all.insert(loc=3, column='cooccurrence', value=df_obj_all.sum(axis=1, numeric_only=True))
df_amod_all.insert(loc=3, column='cooccurrence', value=df_amod_all.sum(axis=1, numeric_only=True))
df_nounmod_all.insert(loc=3, column='cooccurrence', value=df_nounmod_all.sum(axis=1, numeric_only=True))
df_advmod_verb_all.insert(loc=3, column='cooccurrence', value=df_advmod_verb_all.sum(axis=1, numeric_only=True))
df_advmod_adj_all.insert(loc=3, column='cooccurrence', value=df_advmod_adj_all.sum(axis=1, numeric_only=True))


#各wordpairの構成素の頻度を示す列を追加-----------------------------------

#統語構造別のフレームにwordpairの構成素の頻度を示す列を追加
freq_w1_obj = [Word_freq[w1] for w1 in df_obj_all['w1']]
freq_w2_obj = [Word_freq[w2] for w2 in df_obj_all['w2']]
df_obj_all.insert(loc=4, column="freq_w1", value=freq_w1_obj)
df_obj_all.insert(loc=5, column="freq_w2", value=freq_w2_obj)

freq_w1_amod = [Word_freq[w1] for w1 in df_amod_all['w1']]
freq_w2_amod = [Word_freq[w2] for w2 in df_amod_all['w2']]
df_amod_all.insert(loc=4, column="freq_w1", value=freq_w1_amod)
df_amod_all.insert(loc=5, column="freq_w2", value=freq_w2_amod)

freq_w1_nounmod = [Word_freq[w1] for w1 in df_nounmod_all['w1']]
freq_w2_nounmod = [Word_freq[w2] for w2 in df_nounmod_all['w2']]
df_nounmod_all.insert(loc=4, column="freq_w1", value=freq_w1_nounmod)
df_nounmod_all.insert(loc=5, column="freq_w2", value=freq_w2_nounmod)

freq_w1_advmod_verb = [Word_freq[w1] for w1 in df_advmod_verb_all['w1']]
freq_w2_advmod_verb = [Word_freq[w2] for w2 in df_advmod_verb_all['w2']]
df_advmod_verb_all.insert(loc=4, column="freq_w1", value=freq_w1_advmod_verb)
df_advmod_verb_all.insert(loc=5, column="freq_w2", value=freq_w2_advmod_verb)

freq_w1_advmod_adj = [Word_freq[w1] for w1 in df_advmod_adj_all['w1']]
freq_w2_advmod_adj = [Word_freq[w2] for w2 in df_advmod_adj_all['w2']]
df_advmod_adj_all.insert(loc=4, column="freq_w1", value=freq_w1_advmod_adj)
df_advmod_adj_all.insert(loc=5, column="freq_w2", value=freq_w2_advmod_adj)
#語の頻度の集計終了--------------------------------------------------------------------------------



#構成素の統語構造内での語の頻度を示す列を追加-------------------------------------------------------
w1_freq_in_obj = collections.Counter(w1_freq_in_obj)
w2_freq_in_obj = collections.Counter(w2_freq_in_obj)
freq_w1_obj_in_rel = [w1_freq_in_obj[w1] for w1 in df_obj_all['w1']]
freq_w2_obj_in_rel = [w2_freq_in_obj[w2] for w2 in df_obj_all['w2']]
df_obj_all.insert(loc=6, column="w1_in_rel", value=freq_w1_obj_in_rel)
df_obj_all.insert(loc=7, column="w2_in_rel", value=freq_w2_obj_in_rel)

w1_freq_in_amod = collections.Counter(w1_freq_in_amod)
w2_freq_in_amod = collections.Counter(w2_freq_in_amod)
freq_w1_amod_in_rel = [w1_freq_in_amod[w1] for w1 in df_amod_all['w1']]
freq_w2_amod_in_rel = [w2_freq_in_amod[w2] for w2 in df_amod_all['w2']]
df_amod_all.insert(loc=6, column="w1_in_rel", value=freq_w1_amod_in_rel)
df_amod_all.insert(loc=7, column="w2_in_rel", value=freq_w2_amod_in_rel)

w1_freq_in_nounmod = collections.Counter(w1_freq_in_nounmod)
w2_freq_in_nounmod = collections.Counter(w2_freq_in_nounmod)
freq_w1_nounmod_in_rel = [w1_freq_in_nounmod[w1] for w1 in df_nounmod_all['w1']]
freq_w2_nounmod_in_rel = [w2_freq_in_nounmod[w2] for w2 in df_nounmod_all['w2']]
df_nounmod_all.insert(loc=6, column="w1_in_rel", value=freq_w1_nounmod_in_rel)
df_nounmod_all.insert(loc=7, column="w2_in_rel", value=freq_w2_nounmod_in_rel)

w1_freq_in_advmod_verb = collections.Counter(w1_freq_in_advmod_verb)
w2_freq_in_advmod_verb = collections.Counter(w2_freq_in_advmod_verb)
freq_w1_advmod_verb_in_rel = [w1_freq_in_advmod_verb[w1] for w1 in df_advmod_verb_all['w1']]
freq_w2_advmod_verb_in_rel = [w2_freq_in_advmod_verb[w2] for w2 in df_advmod_verb_all['w2']]
df_advmod_verb_all.insert(loc=6, column="w1_in_rel", value=freq_w1_advmod_verb_in_rel)
df_advmod_verb_all.insert(loc=7, column="w2_in_rel", value=freq_w2_advmod_verb_in_rel)

w1_freq_in_advmod_adj = collections.Counter(w1_freq_in_advmod_adj)
w2_freq_in_advmod_adj = collections.Counter(w2_freq_in_advmod_adj)
freq_w1_advmod_adj_in_rel = [w1_freq_in_advmod_adj[w1] for w1 in df_advmod_adj_all['w1']]
freq_w2_advmod_adj_in_rel = [w2_freq_in_advmod_adj[w2] for w2 in df_advmod_adj_all['w2']]
df_advmod_adj_all.insert(loc=6, column="w1_in_rel", value=freq_w1_advmod_adj_in_rel)
df_advmod_adj_all.insert(loc=7, column="w2_in_rel", value=freq_w2_advmod_adj_in_rel)
#-----------------------------------------------------------------------------------------------------

#DPを示した列を追加
df_obj_all.insert(loc=8, column='DP', value=DP_obj)
df_amod_all.insert(loc=8, column='DP', value=DP_amod)
df_nounmod_all.insert(loc=8, column='DP', value=DP_nounmod)
df_advmod_verb_all.insert(loc=8, column='DP', value=DP_advmod_verb)
df_advmod_adj_all.insert(loc=8, column='DP', value=DP_advmod_adj)


#ジャンルごとの頻度を残した状態のデータフレームを保存
os.chdir(r"C:\Users\wpoto\research\thesis\data\CollocationDataSet")
df_obj_all.to_pickle("obj_genre.pickle")
df_amod_all.to_pickle("amod_genre.pickle")
df_nounmod_all.to_pickle("nounmod_genre.pickle")
df_advmod_verb_all.to_pickle("advmod_verb_genre.pickle")
df_advmod_adj_all.to_pickle("advmod_adj_genre.pickle")



#AMの算出-------------------------------------------------------------------------------------------------------------------------------
print('AMs Calculating ... ')
#コーパス全体の頻度
CorpusSize = genre_token_Series.values.sum()

#AM情報を入れるためのデータフレームを用意
df_amod_AMs = pd.DataFrame({'w1':df_amod_all['w1'],
                           'w2':df_amod_all['w2'], 
                           'relation':df_amod_all['relation'],
                           'cooccurrence':df_amod_all['cooccurrence'],
                           'freq_w1':df_amod_all['freq_w1'],
                           'freq_w2':df_amod_all['freq_w2'],
                           'w1_in_rel':df_amod_all['w1_in_rel'],
                           'w2_in_rel':df_amod_all['w2_in_rel'],
                           'DP':df_amod_all['DP']})


df_obj_AMs = pd.DataFrame({'w1':df_obj_all['w1'],
                           'w2':df_obj_all['w2'], 
                           'relation':df_obj_all['relation'],
                           'cooccurrence':df_obj_all['cooccurrence'],
                           'freq_w1':df_obj_all['freq_w1'],
                           'freq_w2':df_obj_all['freq_w2'],
                           'w1_in_rel':df_obj_all['w1_in_rel'],
                           'w2_in_rel':df_obj_all['w2_in_rel'],
                           'DP':df_obj_all['DP']})

df_nounmod_AMs = pd.DataFrame({'w1':df_nounmod_all['w1'],
                           'w2':df_nounmod_all['w2'], 
                           'relation':df_nounmod_all['relation'],
                           'cooccurrence':df_nounmod_all['cooccurrence'],
                           'freq_w1':df_nounmod_all['freq_w1'],
                           'freq_w2':df_nounmod_all['freq_w2'],
                           'w1_in_rel':df_nounmod_all['w1_in_rel'],
                           'w2_in_rel':df_nounmod_all['w2_in_rel'],
                           'DP':df_nounmod_all['DP']})

df_advmod_verb_AMs = pd.DataFrame({'w1':df_advmod_verb_all['w1'],
                           'w2':df_advmod_verb_all['w2'], 
                           'relation':df_advmod_verb_all['relation'],
                           'cooccurrence':df_advmod_verb_all['cooccurrence'],
                           'freq_w1':df_advmod_verb_all['freq_w1'],
                           'freq_w2':df_advmod_verb_all['freq_w2'],
                           'w1_in_rel':df_advmod_verb_all['w1_in_rel'],
                           'w2_in_rel':df_advmod_verb_all['w2_in_rel'],
                           'DP':df_advmod_verb_all['DP']})

df_advmod_adj_AMs = pd.DataFrame({'w1':df_advmod_adj_all['w1'],
                           'w2':df_advmod_adj_all['w2'], 
                           'relation':df_advmod_adj_all['relation'],
                           'cooccurrence':df_advmod_adj_all['cooccurrence'],
                           'freq_w1':df_advmod_adj_all['freq_w1'],
                           'freq_w2':df_advmod_adj_all['freq_w2'],
                           'w1_in_rel':df_advmod_adj_all['w1_in_rel'],
                           'w2_in_rel':df_advmod_adj_all['w2_in_rel'],
                           'DP':df_advmod_adj_all['DP']})

#データフレームからAMを計算する関数を用意--------------------------------------------------------------------
def AMcalc(df):
    n = df['cooccurrence'].values.sum()
    c1 = df['w1_in_rel'].values
    r1 = df['w2_in_rel'].values
    o11 = df['cooccurrence'].values
    e11 = (r1 * c1) / n

    #Simple AMsの計算
    mi = np.log2(o11/e11)  #MIの計算
    t_score = (o11-e11)/(np.sqrt(o11))  #Tスコアの計算
    mi3 = np.log2(o11**3/e11)  #MI3の計算
    mi2 = np.log2(o11**2/e11)  #MI2の計算
    z_score = (o11 - e11)/np.sqrt(e11)  #Zスコアの計算
    simple_ll = 2*(o11*np.log(o11/e11)-(o11-e11)) #simple_llの計算
    dice = 2 * (o11/(c1+r1))  #Dice係数の計算
    log_dice = 14 + np.log2(dice)  #logDiceの計算

    #contingency tableを使ったAMの計算
    
    #実測値のcontingency table作成
    #                /  collocate present  /  collocate absent  /  total
    # node present  /  o11                /  o12               /  r1
    # node absent  /  o21                /  o22               /  r2
    # total       /  c1                 /  c2                / n

    o12 = r1 - o11
    o21 = c1- o11
    o22 = n - r1 - c1 + o11
    c2 = n - c1
    r2 = n - r1
    #期待値のcontingency table作成
    e12 = (r1*c2)/n
    e21 = (r2*c1)/n
    e22 = (r2*c2)/n

    #log-likelihoodの計算
    log_likelihood = (2*(o11*np.log(o11/e11))) + (2*(o12*np.log(o12/e12))) + (2*(o21*np.log(o21/e21))) + (2*(o22*np.log(o22/e22)))
    #chi-squaredの計算
    chi_squared = ((o11 - e11)**2 / e11) + ((o12 - e12)**2 / e12) + ((o21 - e21)**2 / e21) + ((o22 - e22)**2 / e22)

    df['expected_freq'] = e11
    df['MI'] = mi
    df['MI2'] = mi2
    df['MI3'] = mi3
    df['t_score'] = t_score
    df['z_score'] = z_score
    df['simple_ll'] = simple_ll
    df['Dice'] = dice
    df['logDice'] = log_dice
    df['log_likelihood'] = log_likelihood
    df['chi_squared'] = chi_squared

    return df
#AMを計算する関数終了--------------------------------------------------------------------------------------------


#AMを計算してデータフレームに追加
df_amod_AMs = AMcalc(df_amod_AMs)
df_obj_AMs = AMcalc(df_obj_AMs)
df_nounmod_AMs = AMcalc(df_nounmod_AMs)
df_advmod_verb_AMs = AMcalc(df_advmod_verb_AMs)
df_advmod_adj_AMs = AMcalc(df_advmod_adj_AMs)
print('finish')
#AMの算出終了-------------------------------------------------------------------------------------------------------------------------


#wordpairの構成素のCEFR-Jレベルの情報を付与する-------------------------------------------------------
#各単語のCEFR-Jレベルの辞書を用意
CEFR_VERB = {}
CEFR_ADJ = {}
CEFR_NOUN = {}
CEFR_ADV = {}
with open("CEFR-J_Wordlist_lempos.csv", "r", encoding="utf-8") as f:
    f.readline()
    for row in f:
        row = row.rstrip()
        row = row.split(',')
        if re.compile("-v$").search(row[0]):
            row[0] = row[0].replace("-v", "")
            CEFR_VERB[row[0]] = row[1]
        elif re.compile("-j$").search(row[0]):
            row[0] = row[0].replace("-j", "")
            CEFR_ADJ[row[0]] = row[1]
        elif re.compile("-n$").search(row[0]):
            row[0] = row[0].replace("-n", "")
            CEFR_NOUN[row[0]] = row[1]
        elif re.compile("-a$").search(row[0]):
            row[0] = row[0].replace("-a", "")
            CEFR_ADV[row[0]] = row[1]


#各構成素をCEFR-J Wordlistと対応付ける
#ADJ+NOUN
w1_CEFR = []
for w1 in df_amod_AMs['w1']:
    try:
        w1_CEFR.append(CEFR_ADJ[w1])
    except KeyError as e:
        w1_CEFR.append("-")
w2_CEFR = []
for w2 in df_amod_AMs['w2']:
    try:
        w2_CEFR.append(CEFR_NOUN[w2])
    except KeyError as e:
        w2_CEFR.append("-")

df_amod_AMs.insert(2, "w1_CEFR", w1_CEFR)
df_amod_AMs.insert(3, "w2_CEFR", w2_CEFR)

#VERB+OBJ
w1_CEFR = []
for w1 in df_obj_AMs['w1']:
    try:
        w1_CEFR.append(CEFR_VERB[w1])
    except KeyError as e:
        w1_CEFR.append("-")
w2_CEFR = []
for w2 in df_obj_AMs['w2']:
    try:
        w2_CEFR.append(CEFR_NOUN[w2])
    except KeyError as e:
        w2_CEFR.append("-")

df_obj_AMs.insert(2, "w1_CEFR", w1_CEFR)
df_obj_AMs.insert(3, "w2_CEFR", w2_CEFR)

#NOUN+NOUN
w1_CEFR = []
for w1 in df_nounmod_AMs['w1']:
    try:
        w1_CEFR.append(CEFR_NOUN[w1])
    except KeyError as e:
        w1_CEFR.append("-")
w2_CEFR = []
for w2 in df_nounmod_AMs['w2']:
    try:
        w2_CEFR.append(CEFR_NOUN[w2])
    except KeyError as e:
        w2_CEFR.append("-")

df_nounmod_AMs.insert(2, "w1_CEFR", w1_CEFR)
df_nounmod_AMs.insert(3, "w2_CEFR", w2_CEFR)

#ADV+VERB
w1_CEFR = []
for w1 in df_advmod_verb_AMs['w1']:
    try:
        w1_CEFR.append(CEFR_ADV[w1])
    except KeyError as e:
        w1_CEFR.append("-")
w2_CEFR = []
for w2 in df_advmod_verb_AMs['w2']:
    try:
        w2_CEFR.append(CEFR_VERB[w2])
    except KeyError as e:
        w2_CEFR.append("-")

df_advmod_verb_AMs.insert(2, "w1_CEFR", w1_CEFR)
df_advmod_verb_AMs.insert(3, "w2_CEFR", w2_CEFR)

#ADV+ADJ
w1_CEFR = []
for w1 in df_advmod_adj_AMs['w1']:
    try:
        w1_CEFR.append(CEFR_ADV[w1])
    except KeyError as e:
        w1_CEFR.append("-")
w2_CEFR = []
for w2 in df_advmod_adj_AMs['w2']:
    try:
        w2_CEFR.append(CEFR_ADJ[w2])
    except KeyError as e:
        w2_CEFR.append("-")

df_advmod_adj_AMs.insert(2, "w1_CEFR", w1_CEFR)
df_advmod_adj_AMs.insert(3, "w2_CEFR", w2_CEFR)
#wordpairの構成素のCEFR-Jレベルの情報の付与終了-------------------------------------------------------


#データフレームを保存
df_amod_AMs.to_pickle("amod_AMs_all.pickle")
df_obj_AMs.to_pickle("obj_AMs_all.pickle")
df_nounmod_AMs.to_pickle("nounmod_AMs_all.pickle")
df_advmod_verb_AMs.to_pickle("advmod_verb_AMs_all.pickle")
df_advmod_adj_AMs.to_pickle("advmod_adj_AMs_all.pickle")
#全フレームを結合したものも保存
whole_df = pd.concat([df_amod_AMs, df_obj_AMs, df_nounmod_AMs, df_advmod_verb_AMs, df_advmod_adj_AMs])
whole_df.to_pickle("WordPair_AllData.pickle")


#実測値頻度が期待値頻度よりも少ないものを削除したデータフレームを作成し保存
df_amod_AMs.reset_index(drop=True,inplace=True)
df_amod_AMs.drop(index=df_amod_AMs.index[[df_amod_AMs['cooccurence'] < df_amod_AMs['expected_freq']]], inplace=True)
df_obj_AMs.reset_index(drop=True,inplace=True)
df_obj_AMs.drop(index=df_obj_AMs.index[[df_obj_AMs['cooccurence'] < df_obj_AMs['expected_freq']]], inplace=True)
df_nounmod_AMs.reset_index(drop=True,inplace=True)
df_nounmod_AMs.drop(index=df_nounmod_AMs.index[[df_nounmod_AMs['cooccurence'] < df_nounmod_AMs['expected_freq']]], inplace=True)
df_advmod_verb_AMs.reset_index(drop=True,inplace=True)
df_advmod_verb_AMs.drop(index=df_advmod_verb_AMs.index[[df_advmod_verb_AMs['cooccurence'] < df_advmod_verb_AMs['expected_freq']]], inplace=True)
df_advmod_adj_AMs.reset_index(drop=True,inplace=True)
df_advmod_adj_AMs.drop(index=df_advmod_adj_AMs.index[[df_advmod_adj_AMs['cooccurence'] < df_advmod_adj_AMs['expected_freq']]], inplace=True)
df_amod_AMs.to_pickle("amod_collocation.pickle")
df_obj_AMs.to_pickle("obj_collocation.pickle")
df_nounmod_AMs.to_pickle("nounmod_collocation.pickle")
df_advmod_verb_AMs.to_pickle("advmod_verb_collocation_all.pickle")
df_advmod_adj_AMs.to_pickle("advmod_adj_collocation_all.pickle")
#全フレームを結合したものも保存
collocation_df = pd.concat([df_amod_AMs, df_obj_AMs, df_nounmod_AMs, df_advmod_verb_AMs, df_advmod_adj_AMs])
collocation_df.to_pickle("CollocationDataSet.pickle")


#CEFR-J Wordlistにはない単語が入ったものを削除したデータフレーム
df_obj_AMs_CFER_alone = df_obj_AMs.drop(index=df_obj_AMs.index[(df_obj_AMs["w1_CEFR"] == "-") | (df_obj_AMs["w2_CEFR"] == "-")])
df_amod_AMs_CFER_alone = df_amod_AMs.drop(index=df_amod_AMs.index[(df_amod_AMs["w1_CEFR"] == "-") | (df_amod_AMs["w2_CEFR"] == "-")])
df_nounmod_AMs_CFER_alone = df_nounmod_AMs.drop(index=df_nounmod_AMs.index[(df_nounmod_AMs["w1_CEFR"] == "-") | (df_nounmod_AMs["w2_CEFR"] == "-")])
df_advmod_verb_AMs_CFER_alone = df_advmod_verb_AMs.drop(index=df_advmod_verb_AMs.index[(df_advmod_verb_AMs["w1_CEFR"] == "-") | (df_advmod_verb_AMs["w2_CEFR"] == "-")])
df_advmod_adj_AMs_CFER_alone = df_advmod_adj_AMs.drop(index=df_advmod_adj_AMs.index[(df_advmod_adj_AMs["w1_CEFR"] == "-") | (df_advmod_adj_AMs["w2_CEFR"] == "-")])


df_obj_AMs_CFER_alone.to_pickle("obj_AMs_CEFR.pickle")
df_amod_AMs_CFER_alone.to_pickle("amod_AMs_CEFR.pickle")
df_nounmod_AMs_CFER_alone.to_pickle("nounmod_AMs_CEFR.pickle")
df_advmod_verb_AMs_CFER_alone.to_pickle("advmod_verb_AMs_CEFR.pickle")
df_advmod_adj_AMs_CFER_alone.to_pickle("advmod_adj_AMs_CEFR.pickle")