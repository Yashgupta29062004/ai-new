from typing import Optional
import sys
from pathlib import Path

# Fix: Ensure the path points to the root so 'app' is found
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.youtube import YouTubeScraper
# Fix: Match your actual folder 'databases' and file 'repositry'
from app.databases.repositry import Repository

TRANSCRIPT_UNAVAILABLE_MARKER = "__UNAVAILABLE__"

def process_youtube_transcripts(limit: Optional[int] = None) -> dict:
    scraper = YouTubeScraper()
    repo = Repository()
    
    # This pulls videos where transcript IS NULL
    videos = repo.get_youtube_videos_without_transcript(limit=limit)
    
    processed = 0
    unavailable = 0
    
    if not videos:
        print(" No new videos found that need transcripts.")
        return {"total": 0, "processed": 0, "unavailable": 0, "failed": 0}

    print(f" Found {len(videos)} videos to process...")

    for video in videos:
        print(f" Fetching transcript for: {video.title[:50]}...")
        try:
            # Assumes your YouTubeScraper has a get_transcript method
            transcript_result = scraper.get_transcript(video.video_id)
            
            if transcript_result and hasattr(transcript_result, 'text'):
                repo.update_youtube_video_transcript(video.video_id, transcript_result.text)
                print(f" Success: Saved transcript for {video.video_id}")
                processed += 1
            else:
                repo.update_youtube_video_transcript(video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER)
                print(f"⚠️ Unavailable: No transcript found for {video.video_id}")
                unavailable += 1
                
        except Exception as e:
            # We mark as unavailable so the script doesn't keep retrying the same broken video
            repo.update_youtube_video_transcript(video.video_id, TRANSCRIPT_UNAVAILABLE_MARKER)
            unavailable += 1
            print(f" Error processing {video.video_id}: {e}")
    
    return {
        "total": len(videos),
        "processed": processed,
        "unavailable": unavailable,
        "failed": 0 # (Included for compatibility with your return dict)
    }

if __name__ == "__main__":
    print(" Starting YouTube Transcript Processing...")
    result = process_youtube_transcripts()
    print(f"\n--- Final Stats ---")
    print(f"Total videos: {result['total']}")
    print(f"Processed:    {result['processed']}")
    print(f"Unavailable:  {result['unavailable']}")