import streamlit as st
import preprocessor
import functions
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image

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
    .stButton>button {
        background-color: #25D366;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        border: 2px solid #075E54;
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

# Sidebar with WhatsApp theme colors
with st.sidebar:
    st.title('💬 WhatsApp Chat Analyzer')
    
    # File uploader with clearer instructions
    uploaded_file = st.file_uploader("Upload your chat export (without media)", type=["txt"])
    
    # User selection will only appear after file upload
    if uploaded_file is not None:
        # DataFrame
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode('utf-8')
        df = preprocessor.preprocess(data)
        # print(df['user'])

        # fetch unique user
        user_details = df['user'].unique().tolist()
        # remove Group Notifications
        if 'Group Notification' in user_details:
            user_details.remove('Group Notification')
        # sorting list
        user_details.sort()
        # insert overall option
        user_details.insert(0, 'Overall')
        
        st.markdown("### Select Participant")
        selected_user = st.selectbox('Show analysis for:', user_details)
        
        # Make the button more prominent
        analyze_button = st.button('🔍 Analyze Now!')
    else:
        analyze_button = False

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

# Analysis section
elif analyze_button:
    num_msgs, num_med, link = functions.fetch_stats(selected_user, df)
    
    # Create dashboard header
    st.markdown(f"# WhatsApp Insights: {'Overall' if selected_user == 'Overall' else selected_user}")
    st.markdown(f"*Analysis of {num_msgs} messages*")
    
    # Stats cards in a more visually appealing format
    st.markdown("## 📊 Chat Statistics")
    stats_cols = st.columns(3)
    
    with stats_cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <h3>Total Messages</h3>
            <h2>{num_msgs}</h2>
        </div>
        """, unsafe_allow_html=True)
        
    with stats_cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <h3>Media Shared</h3>
            <h2>{num_med}</h2>
        </div>
        """, unsafe_allow_html=True)
        
    with stats_cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <h3>Links Shared</h3>
            <h2>{link}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Activity over time - using tabs for organization
    st.markdown("## 📅 Activity Timeline")
    
    timeline_tabs = st.tabs(["Monthly Activity", "Daily Activity"])
    
    with timeline_tabs[0]:
        # Monthly timeline with improved matplotlib
        timeline = functions.monthly_timeline(selected_user, df)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['time'], timeline['msg'], marker='o', linewidth=2, color='#25D366')
        ax.set_title('Messages per Month')
        ax.set_xlabel('Month')
        ax.set_ylabel('Message Count')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Highlight max point
        max_idx = timeline['msg'].idxmax()
        max_x = timeline['time'][max_idx]
        max_y = timeline['msg'][max_idx]
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
        timeline = functions.daily_timeline(selected_user, df)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['date'], timeline['msg'], marker='.', linewidth=1.5, color='#128C7E')
        ax.set_title('Messages per Day')
        ax.set_xlabel('Date')
        ax.set_ylabel('Message Count')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

    # Activity maps with improved colors
    st.markdown("## 🗓️ Activity Patterns")
    
    active_cols = st.columns(2)
    
    active_month_df, month_list, month_msg_list, active_day_df, day_list, day_msg_list = functions.activity_map(selected_user, df)
    
    with active_cols[0]:
        # Month activity with improved matplotlib
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Plot all bars
        bars = ax.bar(active_month_df['month'], active_month_df['msg'], color='#34B7F1')
        
        # Highlight max and min
        max_idx = month_msg_list.index(max(month_msg_list))
        min_idx = month_msg_list.index(min(month_msg_list))
        
        # Change colors for max and min
        bars[month_list.index(month_list[max_idx])].set_color('#25D366')
        bars[month_list.index(month_list[min_idx])].set_color('#FF6B6B')
        
        ax.set_title('Monthly Activity Pattern')
        ax.set_xlabel('Month')
        ax.set_ylabel('Message Count')
        
        # Add a legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#34B7F1', label='Regular'),
            Patch(facecolor='#25D366', label='Most Active'),
            Patch(facecolor='#FF6B6B', label='Least Active')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
    with active_cols[1]:
        # Day activity with improved matplotlib
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Plot all bars
        bars = ax.bar(active_day_df['day'], active_day_df['msg'], color='#34B7F1')
        
        # Highlight max and min
        max_idx = day_msg_list.index(max(day_msg_list))
        min_idx = day_msg_list.index(min(day_msg_list))
        
        # Change colors for max and min
        bars[day_list.index(day_list[max_idx])].set_color('#25D366')
        bars[day_list.index(day_list[min_idx])].set_color('#FF6B6B')
        
        ax.set_title('Daily Activity Pattern')
        ax.set_xlabel('Day of Week')
        ax.set_ylabel('Message Count')
        
        # Add a legend
        legend_elements = [
            Patch(facecolor='#34B7F1', label='Regular'),
            Patch(facecolor='#25D366', label='Most Active'),
            Patch(facecolor='#FF6B6B', label='Least Active')
        ]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        st.pyplot(fig)

    # Most chatty users section (only in Overall mode)
    if selected_user == 'Overall':
        st.markdown("## 👥 Participant Activity")
        
        x, percent = functions.most_chaty(df)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Bar chart with improved matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            
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
            # Pie chart for percentage distribution
            fig, ax = plt.subplots(figsize=(8, 8))
            
            # Get top 5 participants for pie chart to avoid cluttering
            top_percent = percent.nlargest(5, 'percentage')
            
            if len(percent) > 5:
                # Add "Others" category
                others_sum = percent.nsmallest(len(percent) - 5, 'percentage')['percentage'].sum()
                others_df = pd.DataFrame({'percentage': [others_sum]}, index=['Others'])
                top_percent = pd.concat([top_percent, others_df])
            
            # Create pie chart
            pie_wedges, texts, autotexts = ax.pie(
                top_percent['percentage'], 
                labels=top_percent.index, 
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'edgecolor': 'white'},
                textprops={'fontsize': 9},
                colors=plt.cm.viridis(np.linspace(0, 0.8, len(top_percent)))
            )
            
            # Format text for better visibility
            for text in autotexts:
                text.set_color('white')
                text.set_fontweight('bold')
            
            ax.set_title('Contribution Percentage')
            ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Show percentage table
            st.markdown("### Detailed Percentage")
            st.dataframe(percent, use_container_width=True)

    # Word cloud with improved styling
    st.markdown("## 🔤 Word Analysis")
    
    wordcloud_cols = st.columns([3, 1])
    
    with wordcloud_cols[0]:
        df_wc = functions.create_wordcloud(selected_user, df)
        
        # Use matplotlib for the wordcloud but with better styling
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout()
        
        st.pyplot(fig)
    
    with wordcloud_cols[1]:
        st.markdown("""
        ### Most Common Words
        
        The word cloud shows the most frequently used words in your conversation, with larger text indicating higher frequency.
        
        *Common words like 'and', 'the', etc. are filtered out.*
        
        **Try selecting different participants to see how their vocabulary differs!**
        """)
    
    # Footer with attribution
    st.markdown("""
    <div style='background-color:#075E54; padding:15px; border-radius:10px; text-align:center; margin-top:50px;'>
        <span style='color:white; font-size:12px;'>© 2021-2025, All rights reserved to Santosh Sahoo. Enhanced by Claude.</span>
    </div>
    """, unsafe_allow_html=True)
else:
    # This handles the case where the file is uploaded but not yet analyzed
    pass