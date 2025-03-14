import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import pandas as pd

# Set page config for a wider layout and custom title/icon
st.set_page_config(
    page_title="WhatsApp Chat Insights",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve appearance
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .sidebar .sidebar-content {
        background-color: #25D366;
        color: white;
    }
    h1, h2, h3 {
        color: #075E54;
    }
    
    .stat-card {
        background-color: #DCF8C6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .stat-card h3 {
        color: #075E54;
        margin-bottom: 10px;
    }
    .stat-card h2 {
        color: #128C7E;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title('💬 WhatsApp Chat Analyzer')


uploaded_file = st.sidebar.file_uploader("Choose a file")

# Main content
if uploaded_file is None:
    # Create a more engaging landing page
    st.markdown("# 📱 Welcome to WhatsApp Chat Insights!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Discover what your WhatsApp conversations reveal!
        
        This tool analyzes your WhatsApp chats and generates visualizations to help you understand:
        
        * 📊 Who sends the most messages
        * 🕰️ When conversations are most active
        * 🔤 Most commonly used words and phrases
        * 📅 How chat patterns change over time
        * 🖼️ Media sharing patterns
        
        ### How to use:
        1. Export a WhatsApp chat (Settings → Chat → Export Chat → Without Media)
        2. Upload the .txt file using the sidebar
        3. Click "Analyze Now" to see your insights!
        
        **Your data remains private and is not stored anywhere.**
        """)
    
    with col2:
        # Placeholder for app info
        st.markdown("### Example Insights")
        st.markdown("""
        * Discover which days of the week are most active
        * See your chat activity over months
        * Find out who participates most in group chats
        * Learn which words are used most frequently
        
        Upload your chat to get started!
        """)
        # Display WhatsApp-like icon/bubble
        st.markdown("""
        <div style="background-color: #DCF8C6; border-radius: 15px; padding: 20px; text-align: center; margin-top: 20px;">
            <h3 style="color: #075E54;">📱 WhatsApp Chat Analyzer</h3>
            <p style="color: #128C7E;">Upload a chat to begin!</p>
        </div>
        """, unsafe_allow_html=True)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("🔍 Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        
        # Create dashboard header
        st.markdown(f"# WhatsApp Insights: {'Overall' if selected_user == 'Overall' else selected_user}")

        # Stats cards in a more visually appealing format
        st.markdown("## 📊 Chat Statistics")

        stats_cols = st.columns(3)
    
        with stats_cols[0]:
            st.markdown(f"""
            <div class="stat-card">
                <h3>Total Messages</h3>
                <h2>{num_messages}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[1]:
            st.markdown(f"""
            <div class="stat-card">
                <h3>Media Shared</h3>
                <h2>{num_media_messages}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with stats_cols[2]:
            st.markdown(f"""
            <div class="stat-card">
                <h3>Links Shared</h3>
                <h2>{num_links}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Activity over time - using tabs for organization
        st.markdown("## 📅 Activity Timeline")
    
        timeline_tabs = st.tabs(["Monthly Activity", "Daily Activity"])
        
        with timeline_tabs[0]:
            # Monthly timeline with improved matplotlib
            timeline = helper.monthly_timeline(selected_user, df)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(timeline['time'], timeline['message'], marker='o', linewidth=2, color='#25D366')
            ax.set_title('Messages per Month')
            ax.set_xlabel('Month')
            ax.set_ylabel('Message Count')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Highlight max point
            max_idx = timeline['message'].idxmax()
            max_x = timeline['time'][max_idx]
            max_y = timeline['message'][max_idx]
            ax.scatter([max_x], [max_y], color='#075E54', s=100, zorder=5)
            ax.annotate(f'Max: {max_y}', 
                    (max_x, max_y), 
                    textcoords="offset points", 
                    xytext=(0,10), 
                    ha='center')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        with timeline_tabs[1]:
            # Daily timeline with improved matplotlib
            timeline = helper.daily_timeline(selected_user, df)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(timeline['only_date'], timeline['message'], marker='.', linewidth=1.5, color='#075E54')
            ax.set_title('Messages per Day')
            ax.set_xlabel('Date')
            ax.set_ylabel('Message Count')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        # activity map
        st.markdown("## 🗓️ Activity Patterns")
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most Chatty Day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most Chatty Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('😆 Most Chatty Users')
            x,new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots(figsize=(10, 10))
            
                # Create colormap for gradient
                colors = plt.cm.viridis(np.linspace(0, 0.8, len(x)))
                
                # Plot bars with colormap
                bars = ax.bar(x.index, x.values, color=colors)
                
                ax.set_title('Messages by Participant')
                ax.set_xlabel('Participant')
                ax.set_ylabel('Number of Messages')
                
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title(" 🔤 Wordcloud")
        wordcloud_cols = st.columns([3, 1])

        with wordcloud_cols[0]:
            
            df_wc = helper.create_wordcloud(selected_user,df)
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout()
            
            st.pyplot(fig)

        with wordcloud_cols[1]:
            st.markdown("""
            
            The word cloud shows the most frequently used words in your conversation, with larger text indicating higher frequency.
            
            *Common words like 'and', 'the', etc. are filtered out.*
            
            **Try selecting different participants to see how their vocabulary differs!**
            """)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("✨ Emoji Analysis")

        col1,col2 = st.columns(2)

        with col1:
            emoji_df.columns = ['emoji', 'count']
            emoji_df.reset_index(drop=True, inplace=True)
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f")
            st.pyplot(fig)

        # Footer with attribution
        st.markdown("""
        <div style='background-color:#075E54; padding:15px; border-radius:10px; text-align:center; margin-top:50px;'>
            <span style='color:white; font-size:12px;'>© 2021-2025, All rights reserved to Santosh Sahoo.</span>
        </div>
        """, unsafe_allow_html=True)










