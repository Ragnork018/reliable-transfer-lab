import streamlit as st,pandas as pd,matplotlib.pyplot as plt
from reliable_lab.core import ChannelConfig,compare_protocols
st.set_page_config(page_title='Reliable Transfer Lab',page_icon='⌁',layout='wide')
st.markdown("<style>.stApp{background:#10171d;color:#e7eef4}.stMetric{background:#19242d;padding:14px;border:1px solid #30404a;border-radius:8px}h1,h2{letter-spacing:-.04em}</style>",unsafe_allow_html=True)
st.title('Reliable Transfer Lab');st.caption('PACKET RELIABILITY / ARQ PROTOCOL ANALYSIS')
st.warning('This is a deterministic simulation dashboard, not a live network monitor. Goodput is measured per simulation round, not in real-world bits per second.')
with st.sidebar:
 st.subheader('Channel conditions');messages=st.slider('Messages',20,500,120,10);payload=st.select_slider('Payload bytes',[64,128,256,512,1024,2048],value=512);window=st.slider('Window size',1,32,8)
 loss=st.slider('Data loss probability',0.0,.5,.08,.01);ack=st.slider('ACK loss probability',0.0,.5,.04,.01);corrupt=st.slider('Corruption probability',0.0,.2,.01,.005);dup=st.slider('Duplication probability',0.0,.2,.01,.005);seed=st.number_input('Seed',0,1_000_000,17)
if st.button('Run experiment',type='primary'):
 c=ChannelConfig(loss,ack,corrupt,dup,50,int(seed));rs=compare_protocols(messages=messages,payload_bytes=payload,window=window,config=c);st.session_state['results']=[r.to_dict() for r in rs]
if 'results' in st.session_state:
 d=pd.DataFrame(st.session_state['results']);a,b,c=st.columns(3)
 for col,(_,r) in zip([a,b,c],d.iterrows()):col.metric(r['protocol'],f"{r['reliability']:.1%} delivered",f"{r['retransmissions']} retransmissions")
 fig,ax=plt.subplots();ax.bar(d['protocol'],d['goodput_per_round']);ax.set_title('Delivered payload bytes per simulation round');ax.set_ylabel('Bytes / round');ax.tick_params(axis='x',rotation=15);st.pyplot(fig)
 st.dataframe(d[['protocol','delivered_messages','data_attempts','ack_attempts','data_drops','ack_drops','corruptions','duplicates','rounds','goodput_per_round']],use_container_width=True)
 st.download_button('Download experiment JSON',pd.DataFrame(st.session_state['results']).to_json(orient='records',indent=2),'experiment.json','application/json')
