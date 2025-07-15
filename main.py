import os
import shutil
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message, Document
from pyromod import listen
from yt_dlp import YoutubeDL
import yt_dlp
import sys

API_ID = "26468828"
API_HASH = "4693513c08d1ac6af15f95b116c29478"
BOT_TOKEN = "7691787880:AAFQN39ptfVyjQbKA4NXrid7AHJZbcoOwcM"

app = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store user states and file paths
user_states = {}
cookies_folder = "cookies"
cookies_file_path = os.path.join(cookies_folder, "cookies.txt")
links_folder = "links"
links_file_path = os.path.join(links_folder, "urls.txt")

# Ensure the cookies and links folders exist
os.makedirs(cookies_folder, exist_ok=True)
os.makedirs(links_folder, exist_ok=True)

@app.on_message(filters.command(["start"]))
async def start_command(client: Client, message: Message):
    await message.reply_text("╭──╯ . . . . .\n**    👋 Hello! Welcome....\n•·•·•·•·•·•·•·•·•·••\n🌟 𝕀 𝕒𝕞 𝕒 𝕪𝕠𝕦𝕥𝕦𝕓𝕖 𝕧𝕚𝕕𝕖𝕠 𝔻𝕠𝕨𝕟𝕝𝕠𝕒𝕕𝕖𝕣 𝔹𝕠𝕥. 𝕊𝕖𝕟𝕕 𝕞𝕖 𝕒 𝕧𝕚𝕕𝕖𝕠 𝕌ℝ𝕃 𝕥𝕠 𝕤𝕥𝕒𝕣𝕥.\n•·•·•·•·•·•·•·•·•·••\n┏━━━━━•❃°•°❀°•°❃•━━━━━┓\n❤️‍🩹 **ᴊᴏɪɴ ᴏᴜʀ <a href='https://t.me/scammer_botxz1'>ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ</a>** \n💗 ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href='https://t.me/Scammer_botxz'>😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~ </a>\n┗━━━━━•❃°•°❀°•°❃•━━━━━┛\n       . . . . . ╰──╮")

@app.on_message(filters.command(["c"]))
async def update_cookies_command(client: Client, message: Message):
    # Clear the cookies folder
    shutil.rmtree(cookies_folder)
    os.makedirs(cookies_folder, exist_ok=True)
    
    await message.reply_text("Please send the new `cookies.txt` file.")

@app.on_message(filters.command("Stop"))
async def restart_handler(_, m):
    await m.reply_text("🚯 **ꜱᴛᴏᴘᴘᴇᴅ** 🚯", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@app.on_message(filters.command(["txt"]))
async def txt_command(client: Client, message: Message):
    # Clear the links folder
    shutil.rmtree(links_folder)
    os.makedirs(links_folder, exist_ok=True)
    
    await message.reply_text("Please send the text file containing YouTube URLs.")
    
@app.on_message(filters.command(["extract"]))
async def extract_command(client: Client, message: Message):
    editable = await message.reply_text("Please send the URL of the YouTube playlist.")
    input: Message = await app.listen(editable.chat.id)
    playlist_url = input.text
    await message.reply_text("extracting...")
    video_links, playlist_name = get_video_links(playlist_url)
    if video_links:
        ex_filename = f"{playlist_name}.txt"
        save_links_to_file(video_links, ex_filename)
        # 
        await message.reply_document(ex_filename, caption='Extraction done there is your file.\n Thanks for choosing me!')
        os.remove(ex_filename)
    else:
        await message.reply_text("No video links found")
    
    

@app.on_message(filters.document & ~filters.command(["start", "c", "txt"]))
async def handle_document(client: Client, message: Message):
    document: Document = message.document
    if document.file_name == "cookies.txt":
        await client.download_media(message, file_name=cookies_file_path)
        await message.reply_text("`cookies.txt` file has been updated successfully.")
    elif document.file_name.endswith(".txt"):
        file_path = os.path.join(links_folder, document.file_name)
        await client.download_media(message, file_name=file_path)
        await message.reply_text("Text file received. Now, please send me the desired resolution\n**╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━➣\n┣⪼ 240\n┣⪼ 360\n┣⪼ 480\n┣⪼ 720\n┣⪼ 1080\n┣⪼ 1920\n╰━━⌈⚡[😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~]⚡⌋━━➣ **")
        
        # Listen for the resolution
        resolution_message: Message = await app.listen(message.chat.id)
        if resolution_message.text.isdigit():
            resolution = resolution_message.text
            await process_text_file(client, message, file_path, resolution)
        else:
            await message.reply_text("Invalid resolution. Please enter a numeric value.")

@app.on_message(filters.text & ~filters.command(["start", "c", "txt"]))
async def handle_message(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text

    if user_id not in user_states:
        # First message: Assume it's the video URL
        user_states[user_id] = {'stage': 'video_url', 'video_url': text}
        await message.reply_text("Got it! Now, please send me the desired resolution\n**╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━➣\n┣⪼ 240\n┣⪼ 360\n┣⪼ 480\n┣⪼ 720\n┣⪼ 1080\n┣⪼ 1920\n╰━━⌈⚡[😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~]⚡⌋━━➣ **")
    elif user_states[user_id]['stage'] == 'video_url':
        # Second message: Assume it's the resolution
        user_states[user_id]['resolution'] = text
        user_states[user_id]['stage'] = 'downloading'

        video_url = user_states[user_id]['video_url']
        resolution = user_states[user_id]['resolution']

        try:
            resolution = int(resolution)
            status_message = await message.reply_text("Downloading...⚡⚡⚡ \n•·•·•·•·•·•·•·•·•·••\n**ᴊᴏɪɴ ᴏᴜʀ <a href='https://t.me/scammer_botxz1'>ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ</a>**\n•·•·•·•·•·•·•·•·•·••")

            title, download_folder = await download_videos(video_url, resolution, status_message)
            
            # Define the file paths
            video_file = os.path.join(download_folder, f'{title}_video_{resolution}.mp4')
            audio_file = os.path.join(download_folder, f'{title}_audio_{resolution}.webm')
            output_file = os.path.join(download_folder, f'final_{title}.mp4')  # Final output video

            # Extract thumbnail and duration
            thumbnail, duration = await extract_thumbnail_and_duration(video_file, download_folder)

            # Merge the audio and video
            await merge_audio_video(video_file, audio_file, output_file, status_message)

            # Delete the original video and audio files
            await delete_files(video_file, audio_file, status_message)

            # Send the video to the user
            await send_video(client, message, output_file, status_message, title, thumbnail, duration)

            # Clear the download folder
            await clear_download_folder(download_folder)

        except ValueError:
            await message.reply_text("Invalid resolution. Please enter a numeric value.")
        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")

        # Clear user state after processing
        user_states.pop(user_id, None)

async def process_text_file(client: Client, message: Message, file_path: str, resolution: str):
    try:
        with open(file_path, "r") as file:
            urls = file.readlines()
            for url in urls:
                url = url.strip()
                if url:
                    status_message = await message.reply_text(f"Downloading {url} with resolution {resolution}p...")

                    try:
                        title, download_folder = await download_videos(url, resolution, status_message)
                        
                        # Define the file paths
                        video_file = os.path.join(download_folder, f'{title}_video_{resolution}.mp4')
                        audio_file = os.path.join(download_folder, f'{title}_audio_{resolution}.webm')
                        output_file = os.path.join(download_folder, f'final_{title}.mp4')  # Final output video

                        # Extract thumbnail and duration
                        thumbnail, duration = await extract_thumbnail_and_duration(video_file, download_folder)

                        # Merge the audio and video
                        await merge_audio_video(video_file, audio_file, output_file, status_message)

                        # Delete the original video and audio files
                        await delete_files(video_file, audio_file, status_message)

                        # Send the video to the user
                        await send_video(client, message, output_file, status_message, title, thumbnail, duration)
                        await status_message.delete(True)

                        # Clear the download folder
                        await clear_download_folder(download_folder)

                    except Exception as e:
                        await message.reply_text(f"An error occurred while downloading {url}: {e}")

        os.remove(file_path)
    except Exception as e:
        await message.reply_text(f"Invalid file input. Error: {e}")
        os.remove(file_path)

async def download_videos(video_url, resolution, status_message):
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)

    await status_message.edit("Getting video information...")
    with YoutubeDL({'quiet': True, 'cookiefile': cookies_file_path}) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        title = info_dict.get('title', 'untitled')

    webm_audio_options = {
        'format': 'bestaudio[ext=webm]/bestaudio',
        'outtmpl': os.path.join(download_folder, f'{title}_audio_{resolution}.webm'),
        'quiet': False,
        'cookiefile': cookies_file_path
    }

    mp4_video_options = {
        'format': f'bestvideo[ext=mp4][height={resolution}][vcodec!^=av01]/bestvideo[ext=mp4][vcodec!^=av01]',
        'outtmpl': os.path.join(download_folder, f'{title}_video_{resolution}.mp4'),
        'quiet': False,
        'cookiefile': cookies_file_path
    }

    await status_message.edit(f"Downloading WebM audio for '{title}' with resolution {resolution}p...")
    with YoutubeDL(webm_audio_options) as ydl:
        ydl.download([video_url])

    await status_message.edit(f"Downloading MP4 video for '{title}' with resolution {resolution}p...")
    with YoutubeDL(mp4_video_options) as ydl:
        ydl.download([video_url])

    return title, download_folder

async def extract_thumbnail_and_duration(video_file, download_folder):
    thumbnail = os.path.join(download_folder, "thumbnail.jpg")
    duration = 0

    # Extracting high-quality thumbnail
    command_thumbnail = [
        'ffmpeg',
        '-i', video_file,
        '-vf', 'thumbnail,scale=320:320',
        '-vframes', '1',
        thumbnail
    ]

    # Extracting duration
    command_duration = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_file
    ]

    try:
        subprocess.run(command_thumbnail, check=True)
        result = subprocess.run(command_duration, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while extracting thumbnail or duration: {e}")

    return thumbnail, int(duration)

async def merge_audio_video(video_file, audio_file, output_file, status_message):
    command = [
        'ffmpeg',
        '-i', video_file,
        '-i', audio_file,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_file
    ]

    try:
        await status_message.edit("Merging audio and video files...")
        subprocess.run(command, check=True)
        print(f"Merge complete! Output file: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

async def delete_files(video_file, audio_file, status_message):
    try:
        await status_message.edit("Cleaning up temporary files...")
        os.remove(video_file)
        os.remove(audio_file)
        print("Original video and audio files deleted successfully.")
    except OSError as e:
        print(f"Error deleting files: {e}")

async def send_video(client, message, output_file, status_message, title, thumbnail, duration):
    video_size = os.path.getsize(output_file)
    video_size_mb = video_size / (1024 * 1024)

    await status_message.edit(f"Ｕｐｌｏａｄｉｎｇ ｖｉｄｅｏ．．．\n┣⪼𝕊𝕚𝕫𝕖: {video_size_mb:.2f} MB\n┣⪼ℙ𝕣𝕠𝕘𝕣𝕖𝕤𝕤 : 0% \n\n💗 ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href='https://t.me/Scammer_botxz'>😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~ </a>\n═════━‧₊˚❀༉‧₊˚.━═════")

    # Track the progress percentage milestones
    progress_milestones = [20, 40, 60, 80, 100]
    current_milestone_index = 0

    async def progress(current, total):
        nonlocal current_milestone_index
        percentage = (current / total) * 100
        if percentage >= progress_milestones[current_milestone_index]:
            await status_message.edit(f"Ｕｐｌｏａｄｉｎｇ ｖｉｄｅｏ．．．\n┣⪼𝕊𝕚𝕫𝕖: {video_size_mb:.2f} MB\n┣⪼ℙ𝕣𝕠𝕘𝕣𝕖𝕤𝕤 : {progress_milestones[current_milestone_index]}%\n\n💗 ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href='https://t.me/Scammer_botxz'>😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~ </a>\n═════━‧₊˚❀༉‧₊˚.━═════")
            current_milestone_index += 1

    try:
        await client.send_video(
            chat_id=message.chat.id,
            video=output_file,
            caption=f"𝑽𝒊𝒅𝒆𝒐 𝑻𝒊𝒕𝒍𝒆 : {title}",  # Add the title as the caption
            supports_streaming=True,
            height=720,
            width=1280,
            thumb=thumbnail,
            duration=duration,
            progress=progress
        )
        await status_message.edit(f"Ｕｐｌｏａｄ ｃｏｍｐｌｅｔｅ！ 🎉\n┣⪼𝕊𝕚𝕫𝕖 : {video_size_mb:.2f} MB\n\n**ᴊᴏɪɴ ᴏᴜʀ <a href='https://t.me/scammer_botxz1'>ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ</a>**\n💗 ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href='https://t.me/Scammer_botxz'>😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~ </a>\n╰━━━━━━━━━━━━━ ❀° ━━━╯シ")
    except Exception as e:
        await status_message.edit(f"An error occurred: {e}")

async def clear_download_folder(download_folder):
    try:
        shutil.rmtree(download_folder)
        print("Download folder cleared successfully.")
    except OSError as e:
        print(f"Error clearing download folder: {e}")
        
def get_video_links(playlist_url):
    # Options for yt-dlp to only extract metadata
    ydl_opts = {
        'extract_flat': True,  # Extract metadata only, no video download
        'quiet': True,         # Suppress output
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(playlist_url, download=False)  # Extract playlist info

    video_links = []
    if 'entries' in playlist_dict:
        for video in playlist_dict['entries']:
            # Construct the full video URL
            video_links.append(f"https://www.youtube.com/watch?v={video['id']}")

    return video_links, playlist_dict.get('title', 'playlist')

def save_links_to_file(links, filename):
    # Write all video links to the specified file
    with open(filename, 'w') as file:
        for link in reversed(links):
            file.write(f"{link}\n")
            

if __name__ == "__main__":
    app.run()
