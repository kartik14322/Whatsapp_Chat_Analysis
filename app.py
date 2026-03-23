import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="WhatsApp Chat Analysis",
    initial_sidebar_state="expanded"
)

# ---------------- GLOBAL STYLE ----------------
mpl.rcParams['font.family'] = 'DejaVu Sans'
mpl.rcParams['font.size'] = 11

# ---------------- RESPONSIVE CSS ----------------
st.markdown("""
<style>

/* Reduce padding on mobile */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* Make all elements full width */
.element-container {
    width: 100% !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📱 WhatsApp Chat Analysis")
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file (.txt)")

heatmap_colors = {
    "Red Blue (Contrast)": "coolwarm",
    "Modern Dark (Viridis)": "viridis",
    "Dark Purple (Magma)": "magma",
}

selected_heatmap = st.sidebar.selectbox(
    "🎨 Select Heatmap Color",
    list(heatmap_colors.keys())
)

# ---------------- MAIN ----------------
if uploaded_file is not None:

    data = uploaded_file.getvalue().decode("utf-8")
    df = preprocessor.preprocess(data)

    st.markdown(
        "<h2 style='text-align:center;color:#FF7F50;'>📱 WhatsApp Chat Data Preview</h2>",
        unsafe_allow_html=True
    )

    st.dataframe(df, use_container_width=True)

    # -------- USER LIST --------
    user_list = df['user'].dropna().unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox(
        "Show Analysis with Respect to:",
        user_list
    )

    if st.sidebar.button("🚀 Show Analysis"):

        # ---------------- TOP STATS ----------------
        st.markdown("## 📊 Top Statistics")

        num_m, words, media, links = helper.fetch_stats(selected_user, df)

        c1, c2 = st.columns(2)
        c3, c4 = st.columns(2)

        c1.metric("💬 Messages", num_m)
        c2.metric("📝 Words", words)
        c3.metric("🖼 Media", media)
        c4.metric("🔗 Links", links)

        # ---------------- MOST BUSY USERS ----------------
        if selected_user == 'Overall':
            st.markdown("## 👥 Most Busy Users")

            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns([2,1])

            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(x.index, x.values, color="#ff4b4b")
            plt.xticks(rotation=45)
            ax.grid(alpha=0.3)

            col1.pyplot(fig, use_container_width=True)
            col2.dataframe(new_df, use_container_width=True)

        # ---------------- COMMON WORDS ----------------
        st.markdown(f"## 🗣 Most Common Words - {selected_user}")

        common_df = helper.most_common_words(selected_user, df)

        if not common_df.empty:

            col1, col2 = st.columns([1,2])

            col1.dataframe(common_df, use_container_width=True)

            fig, ax = plt.subplots(figsize=(6,4.5))
            ax.bar(common_df['Word'], common_df['Count'], color="#4CAF50")
            plt.xticks(rotation=60)

            col2.pyplot(fig, use_container_width=True)

        # ---------------- EMOJI ANALYSIS ----------------
        st.markdown("## 😀 Emoji Analysis")

        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:

            col1, col2 = st.columns([1.7,2.2])

            col1.dataframe(emoji_df, use_container_width=True)

            fig, ax = plt.subplots(figsize=(4,6))
            ax.pie(
                emoji_df[1].head(),
                labels=emoji_df[0].head(),
                autopct="%0.1f%%"
            )

            col2.pyplot(fig, use_container_width=True)

        # ---------------- SENTIMENT ANALYSIS ----------------
        st.markdown("## 😊 Sentiment Analysis")

        sentiment_counts = helper.sentiment_analysis(selected_user, df)

        if not sentiment_counts.empty:

            col1, col2 = st.columns([2,2])

            with col1:
                st.dataframe(sentiment_counts, use_container_width=True)

                fig2, ax2 = plt.subplots(figsize=(10,10))
                ax2.pie(
                    sentiment_counts.values,
                    labels=sentiment_counts.index,
                    autopct="%0.1f%%",
                    textprops={'fontsize': 17}
                )
                st.pyplot(fig2, use_container_width=True)

            with col2:
                fig, ax = plt.subplots(figsize=(2,3.5))
                ax.bar(sentiment_counts.index, sentiment_counts.values)
                ax.set_ylabel("Count")
                ax.set_xticks(range(len(sentiment_counts.index)))
                ax.set_xticklabels(sentiment_counts.index, rotation=45, ha='right')
                st.pyplot(fig, use_container_width=True)

        # ---------------- ACTIVITY MAP ----------------
        st.markdown("## 🗺 Activity Map")

        col1, col2 = st.columns(2)

        with col1:
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(busy_day.index, busy_day.values, color="#6A5ACD")
            plt.xticks(rotation=45)
            st.pyplot(fig, use_container_width=True)

        with col2:
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(busy_month.index, busy_month.values, color="#FF7F50")
            plt.xticks(rotation=45)
            st.pyplot(fig, use_container_width=True)

        # ---------------- HEATMAP ----------------
        st.markdown("## 🔥 Online Activity Heatmap")

        try:
            user_heatmap = df.pivot_table(
                index='day_name',
                columns='period',
                values='message',
                aggfunc='count'
            ).fillna(0)

            fig, ax = plt.subplots(figsize=(8,4))
            sns.heatmap(
                user_heatmap,
                cmap=heatmap_colors[selected_heatmap],
                linewidths=0.5,
                linecolor="white",
                ax=ax
            )

            st.pyplot(fig, use_container_width=True)

        except:
            st.warning("Heatmap data not available")

        # ---------------- TIMELINE ----------------
        st.markdown("## 📈 Timeline Analysis")

        timeline = helper.monthly_timeline(selected_user, df)

        if not timeline.empty:
            timeline['time'] = timeline['time'].astype(str)

            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(timeline['time'], timeline['message'], marker='o')
            plt.xticks(rotation=45)
            st.pyplot(fig, use_container_width=True)

        daily_t = helper.daily_timeline(selected_user, df)

        if not daily_t.empty:
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(daily_t['only_date'], daily_t['message'], marker='o')
            plt.xticks(rotation=45)
            st.pyplot(fig, use_container_width=True)

        # ---------------- PUNCHCARD ----------------
        st.markdown("## 💬 Chat Intensity Punchcard")

        punch_df = helper.get_punchcard_data(selected_user, df)

        if not punch_df.empty:
            fig, ax = plt.subplots(figsize=(10,5))

            ax.scatter(
                punch_df['hour'],
                punch_df['day_name'],
                s=punch_df['message'] * 8,
                alpha=0.6,
                color="#800080"
            )

            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Day of Week")
            ax.grid(True, linestyle='--', alpha=0.4)

            st.pyplot(fig, use_container_width=True)

else:
    st.info(" 👈 Please upload a WhatsApp exported chat file to begin analysis.")



