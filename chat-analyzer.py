import streamlit as st
import function as f
import matplotlib.pyplot as plt
import pandas as pd

## Plotting color
color = "indigo"

st.sidebar.title("Whatsapp chat analyzer")
st.sidebar.warning("This works only on\n12 hour time format.")

uploaded_file = st.sidebar.file_uploader("Choose a chat txt file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = f.data_preprocessing(data)
    # st.dataframe(df)

    user_list = df['sender'].unique().tolist()
    user_list.insert(0, "All")
    selected_user = st.sidebar.selectbox("Select user", user_list)

    ## Adding the button
    if st.sidebar.button("Analyze"):
        st.title("Analysis with repect to {}".format(selected_user))

        if selected_user != "All":
            df = df[df['sender'] == selected_user]
        
        ## Some variables for later use
        words = f.total_words(df)

        ## Defined four columns
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total chats")
            st.title(df.shape[0])
        
        with col2:
            st.header("Total words")
            st.title(len(words))
        
        with col3:
            st.header("Total media")
            st.title(str(f.total_media(df)))
        
        with col4:
            st.header("Total Links")
            st.title(str(f.total_links(df)))
        
        ## Monthly timeline
        st.title("Monthly timeline")
        busy_month = f.busy_month(df)
        busy_month_index = [ str(m) + " " + str(y) for y, m in busy_month.index]
        xs = range(len(busy_month))
        fig, ax = plt.subplots()
        plt.xticks(xs, labels=busy_month_index,rotation='vertical')
        ax.plot( busy_month.values, color=color)
        st.pyplot(fig)


        ## Daily timeline
        st.title("Daily timeline")
        daily_date, daily_value = f.daily_timeline(df)
        fig, ax = plt.subplots()
        ax.plot(daily_date, daily_value, color=color)
        ax.xaxis_date()
        fig.autofmt_xdate(rotation=90)
        st.pyplot(fig)

        ## Busy Month and weeks
        st.title("Most busy week and month")
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("Busy months")
            fig, ax = plt.subplots()
            most_busy_month = f.most_busy_month(df)
            plt.xticks(rotation='vertical')
            ax.bar(most_busy_month.index, most_busy_month.values, color=color)
            st.pyplot(fig)
        
        with col2:
            st.header("Busy weeks")
            fig, ax = plt.subplots()
            most_busy_week = f.most_busy_week(df)
            plt.xticks(rotation='vertical')
            ax.bar(most_busy_week.index, most_busy_week.values, color=color)
            st.pyplot(fig)

        ## Weekly activiy map
        ## Heatmap


        ## Now adding the most busy user.
        if selected_user == "All":
            st.title("Top Busy Users")
            busy_users = f.top_busy_user(df)
            col1 , col2 = st.columns([2,1])

            with col1:
                plt.figure(figsize=(6,6))
                fig, ax = plt.subplots()
                plt.xticks(rotation='vertical')
                ax.bar(busy_users.index, busy_users.values, color=color)
                st.pyplot(fig)
            
            with col2:
                perc_busy_user = f.top_busy_user_percentage(df)
                st.dataframe(perc_busy_user)
        
        ## Top spammer
        spammer = f.get_spammer(df)
        if spammer.shape[0] > 0:
            st.title("Top spammer")
            st.text("Person who deletes the message most")
            col1, col2 = st.columns([1, 1.8], gap='small')
            
            with col1:
                st.header("Spammer list")
                st.dataframe(spammer)

            with col2:
                st.header("Top 10 spammer")
                ten_spammer = spammer.iloc[:10]
                fig, ax = plt.subplots()
                plt.xticks(range(ten_spammer.shape[0]), ten_spammer['Sender'],rotation='vertical')
                ax.set_xlabel("sender deleted messages")
                ax.bar(range(ten_spammer.shape[0]), ten_spammer['Frequency'])
                st.pyplot(fig)


        ## Now plotting the word cloud
        st.title("Word cloud")
        wordcloud = f.create_wordcloud(words)        

        # plot the WordCloud image                      
        plt.figure(figsize = (8, 8), facecolor = None)
        plt.axis("off")
        plt.tight_layout(pad = 4)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud)
        st.pyplot(fig)

        ## Most frequent 
        freq_words = f.most_freq_words(words)
        if freq_words.shape[0] > 0:
            st.title("Most frequent words")
            col1, col2 = st.columns([1, 2], gap="small")
            with col1:
                st.header("Words frequency")
                st.dataframe(freq_words)

            with col2:
                st.header("Words chart")
                fig, ax = plt.subplots()
                plt.xticks(range(freq_words.shape[0]), freq_words['Words'], rotation='vertical')
                ax.bar(height=freq_words['Frequency'], x=range(freq_words.shape[0]), color=color)
                st.pyplot(fig)

        ## Emoji dataframes
        emojis = f.emoji_table(df)
        if emojis.shape[0] > 0:
            st.title("Top emojies Used")
            col1,col2 = st.columns([1, 2])
            with col1:
                st.header("Emoji frequency")
                
                st.dataframe(emojis)
            
            with col2:
                st.header("Emoji distribution")
                fig, ax = plt.subplots()
                plt.title("Emoji Frequency distribution")
                ax.pie(emojis['Frequency'], 
                    explode=[0.1 for i in range(emojis.shape[0])] , labels=emojis['Emoji']);
                st.pyplot(fig)