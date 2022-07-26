import streamlit as st
import pymongo
import numpy as np

#-------------------------------------

#---------------------------
#import stream_page1 as sp1
import os, time

from datetime import datetime
import threading
#------------------------
import pandas as pd
mysymbol = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = mysymbol["trade_setup"]
mycol = mydb["monday"]
#----------------------------------
mydb_nifty = mysymbol["nifty"]

ltp_col =  mydb_nifty["ltp"]
#-----------------------

mydb = mysymbol["ticks"]
fxone_col = mydb["fxone_ticks"]
#-----------------
tab1, tab2, tab3 = st.tabs(["Trade Setup", "Positions", "Option Chain"])
#----------------
with tab1:
#------------------
    with st.form(key='step1'):
        col1, col2,col3,col4,col5,col6 = st.columns(6)
    with col1:
        index = st.selectbox('Index',['NIFTY', 'BANKNIFTY'] , key=1)
    with col2:    
        optype = st.selectbox('Option Type',['CE', 'PE'] , key=2)
    with col3: 
        ordertype= st.selectbox('Order Type' ,['BUY', 'SELL'] ,key=3)
    with col4: 
        strike_sel = st.selectbox('Strike_sel',['ATM-1','ATM', 'ATM+1'] , key=4)
    with col5:
        lot_size = st.number_input('Lot Size', min_value=1, max_value=10, value=1, step=1)
    with col6:    
        st.info("Step 1")
        step1 = st.form_submit_button('Save')
   
        
        

        if step1:
    #step1={'index' : index,'optype' : optype,'ordertype' : ordertype,'strike':strike,'lot_size' : lot_size}
    #mycol.insert_one(step1)
    #st.write(step1)
           step1=[index,optype,ordertype,strike_sel,lot_size]
#------------------------------------------
    with st.form(key='step2'):
        col1, col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            wt = st.number_input('Wait & Trade', min_value=1, max_value=50, value=1, step=1)
        with col2:    
            target = st.number_input('Target', min_value=1, max_value=500, value=50, step=1)
        with col3: 
            sl = st.number_input('StopLose', min_value=1, max_value=25, value=5, step=1)
        with col4: 
            s_ltp_x = st.number_input('Trailing(X) LTP', min_value=2, max_value=10, value=2, step=1)
        with col5:
            s_sl_y = st.number_input('Trailing(Y) SL', min_value=1, max_value=10, value=1, step=1)
        with col6:    
            st.info("Step 2")
            step2 = st.form_submit_button('Save')
#----------------------------------------------------
    if step2:
    #step2={'target' : target,'sl' : sl,'s_ltp' : s_ltp , ' s_sl':s_sl,' s_sl' : s_sl}
    #mycol.insert_one(step2)
    #st.write(step2)
        step2=[wt,target,sl,s_ltp_x , s_sl_y]
#------------------------------------------
    with st.form(key='step3'):
        col1, col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            lock_mtm = st.number_input('Profit Reached', min_value=100, max_value=10000, value=100, step=50)
        with col2:    
            lock_profit = st.number_input('Lock Profit', min_value=50, max_value=5000, value=50, step=1)
        with col3: 
            trail_mtm_x = st.number_input('Trailing X', min_value=100, max_value=5000, value=100, step=1)
        with col4: 
            trial_profit_y = st.number_input('Trailing  Y', min_value=50, max_value=50000, value=50, step=1)
        with col5:
            reentry = st.number_input('Reentry', min_value=1, max_value=10, value=2, step=1)
        with col6:    
            st.info("Step 3")
            step3 = st.form_submit_button('Save')
    if step3:
    #step3={'lock_reached' : lock_reached,'lock_profit' : lock_profit,'trail_mtm' : trail_mtm,
     #      'p_booked':p_booked,'reentry' : reentry}
    #mycol.insert_one(step3)
    #st.write(step3)       
        step3=[lock_mtm,lock_profit,trail_mtm_x,trial_profit_y,reentry]
#--------------------

    if st.button('update'):
        atm_strike = "16700.0"
        myquery = {"_id" : "NIFTY-T1"}
        if (strike_sel=="ATM") & (optype=="CE"):
            x=call_symbol_col.find_one()
            strike_selected=x[atm_strike]
            st.write(strike_selected)
        newvalues= {"index": index,"optype": optype,"ordertype":ordertype ,"strike_sel":strike_sel ,"strike":atm_strike                      ,"symbol":strike_selected,"lot_size": lot_size,"wait&trade":wt,"target": target,"sl": sl,"ref_price": ref_price,"entry_price": entry_price,"s_ltp_x": s_ltp_x, "s_sl_y": s_sl_y,
  "lock_mtm": lock_mtm, "lock_profit": lock_profit,"trail_mtm_x": trail_mtm_x,"trial_profit_y":trial_profit_y}
        mycol.update_one(myquery, newvalues)  
           
                #newvalues = { "$set": { "rprice": ltp} }

        #mycol2.update_one(myquery, newvalues)
        #st.write(newvalues)
    else:
        pass
    
 #--------tab2-----------
with tab2:
#----------------------
    data=mycol.find_one()
    df = pd.DataFrame.from_dict([data])
    df =df[['index','strike','lot_size','target','sl', 'ref_price', 'entry_price', 'LTP', 'MTM','Booked']]
    st.dataframe(df)
#--------tab3-----------
with tab3:
#----------------------    
    st.write('option chain')
 
    
    with st.empty():
        strike_sel=fxone_col.find_one({ "_id" : "strike price"})
        df_strike_sel=list(strike_sel.items())
        df_strike_sel = pd.DataFrame(df_strike_sel)
        df_strike=df_strike_sel.drop(index=df_strike_sel.index[0],axis=0,inplace=True)
        df_strike=df_strike_sel[1].tolist()
        while True:
            call_ltp_select=fxone_col.find_one({ "_id" : "call_ltp"})
            df_call_ltp_select=list(call_ltp_select.items())
            df_call_ltp_select = pd.DataFrame(df_call_ltp_select)
            df_call_ltp=df_call_ltp_select.drop(index=df_call_ltp_select.index[0],axis=0,inplace=True)
            df_call_ltp=df_call_ltp_select[1].tolist()
            #-----------------------------------
            put_ltp_select=fxone_col.find_one({ "_id" : "put_ltp"})
            df_put_ltp_select=list(put_ltp_select.items())
            df_put_ltp_select = pd.DataFrame(df_put_ltp_select)
            df_put_ltp=df_put_ltp_select.drop(index=df_put_ltp_select.index[0],axis=0,inplace=True)
            df_put_ltp=df_put_ltp_select[1].tolist()
            #---------------------------------------------
            optionchain = pd.DataFrame({'Call':df_call_ltp ,'Strike Price':df_strike,'Put':df_put_ltp})
            
            optionchain=optionchain.style.format(precision=2)
            #---------------------------------
            
            #---------------------------------
            st.table(optionchain)
          
            time.sleep(1)    
            
                
   
    
