import tkinter as tk
from tkinter import ttk, messagebox
from googleapiclient.discovery import build
import os
import re
import pandas as pd
from dotenv import load_dotenv

# Çevresel değişkenleri yükle
load_dotenv()
api_key = os.getenv('YOUTUBE_API_KEY')

# YouTube API'yi başlat
youtube = build('youtube', 'v3', developerKey=api_key)

# URL'den Video ID'sini çıkarmak için fonksiyon
def extract_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    return video_id_match.group(1) if video_id_match else None

# Yorumları çekmek için fonksiyon
def get_comments(video_id):
    try:
        comments_data = []
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()

        for item in response['items']:
            comment_info = {
                'ChannelId': item['snippet']['topLevelComment']['snippet']['authorChannelId'].get('value', ''),
                'AuthorDisplayName': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                'VideoId': video_id,
                'LikeCount': item['snippet']['topLevelComment']['snippet']['likeCount'],
                'ReplyCount': item['snippet']['totalReplyCount'],
                'PublishedAt': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                'TextDisplay': item['snippet']['topLevelComment']['snippet']['textDisplay']
            }
            comments_data.append(comment_info)

        return comments_data

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return []

# Yorumları tabloya eklemek için fonksiyon
def display_comments():
    url = entry.get()
    video_id = extract_video_id(url)

    if not video_id:
        messagebox.showwarning("Warning", "Please enter a valid YouTube video URL.")
        return

    global comments_data
    comments_data = get_comments(video_id)
    
    # Mevcut verileri temizle
    for item in tree.get_children():
        tree.delete(item)

    # Yorumları tabloya ekle
    for comment in comments_data:
        tree.insert('', 'end', values=(
            comment['ChannelId'],
            comment['AuthorDisplayName'],
            comment['VideoId'],
            comment['LikeCount'],
            comment['ReplyCount'],
            comment['PublishedAt'],
            comment['TextDisplay']
        ))

# Yorumları CSV dosyasına kaydetme işlevi
def save_to_csv():
    if not comments_data:
        messagebox.showwarning("Warning", "No comments to save.")
        return

    df = pd.DataFrame(comments_data)
    file_path = "comments.csv"
    df.to_csv(file_path, index=False)
    messagebox.showinfo("Success", f"Comments saved to {file_path}")

# Tkinter Arayüzü
window = tk.Tk()
window.title("YouTube Channel Comments Fetcher")
window.geometry("1000x600")

# URL girişi ve düğme
label = tk.Label(window, text="YouTube Channel URL:")
label.pack(pady=5)
entry = tk.Entry(window, width=60)
entry.pack(pady=5)
button = tk.Button(window, text="Fetch Comments", command=display_comments)
button.pack(pady=5)

# Save to CSV düğmesi
save_button = tk.Button(window, text="Save to CSV", command=save_to_csv)
save_button.pack(pady=5)

# Treeview tablosu
columns = ("ChannelId", "AuthorDisplayName", "VideoId", "LikeCount", "ReplyCount", "PublishedAt", "TextDisplay")
tree = ttk.Treeview(window, columns=columns, show='headings')
tree.heading("ChannelId", text="Channel Id")
tree.heading("AuthorDisplayName", text="Author Display Name")
tree.heading("VideoId", text="Video Id")
tree.heading("LikeCount", text="Like Count")
tree.heading("ReplyCount", text="Reply Count")
tree.heading("PublishedAt", text="Published At")
tree.heading("TextDisplay", text="Text Display")

# Sütun genişlikleri ayarla
tree.column("ChannelId", width=150)
tree.column("AuthorDisplayName", width=150)
tree.column("VideoId", width=100)
tree.column("LikeCount", width=80)
tree.column("ReplyCount", width=80)
tree.column("PublishedAt", width=150)
tree.column("TextDisplay", width=300)

tree.pack(fill=tk.BOTH, expand=True)

# Scrollbar ekle
scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

window.mainloop()
