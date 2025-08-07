#!/usr/bin/env python3
"""
LegalCopilot Video QA Frame Extractor
Extracts frames from QA videos for cheap OpenAI analysis
"""

import cv2
import os
import base64
from pathlib import Path
from datetime import datetime
import json

class VideoQAExtractor:
    def __init__(self, qa_folder="QA"):
        self.qa_folder = Path(qa_folder)
        self.frames_folder = self.qa_folder / "frames"
        self.frames_folder.mkdir(exist_ok=True)
        
    def extract_frames(self, video_path, fps_extract=0.5, max_frames=20):
        """
        Extract frames from video
        fps_extract: frames per second to extract (0.5 = 1 frame every 2 seconds)
        max_frames: maximum frames to extract
        """
        print(f"🎥 Processing video: {video_path}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise Exception(f"Could not open video: {video_path}")
            
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"📊 Video info: {duration:.1f}s, {fps:.1f} FPS, {total_frames} total frames")
        
        # Calculate extraction interval
        extract_interval = int(fps / fps_extract)
        frames_extracted = []
        frame_count = 0
        
        # Create output folder for this video
        video_name = Path(video_path).stem
        output_folder = self.frames_folder / video_name
        output_folder.mkdir(exist_ok=True)
        
        while True:
            ret, frame = cap.read()
            if not ret or len(frames_extracted) >= max_frames:
                break
                
            # Extract frame at specified interval
            if frame_count % extract_interval == 0:
                timestamp = frame_count / fps
                frame_filename = f"frame_{len(frames_extracted):03d}_{timestamp:.1f}s.jpg"
                frame_path = output_folder / frame_filename
                
                # Save frame
                cv2.imwrite(str(frame_path), frame)
                frames_extracted.append({
                    "path": str(frame_path),
                    "timestamp": timestamp,
                    "frame_number": frame_count
                })
                
                print(f"📷 Extracted frame {len(frames_extracted)}: {timestamp:.1f}s")
                
            frame_count += 1
            
        cap.release()
        print(f"✅ Extracted {len(frames_extracted)} frames to {output_folder}")
        return frames_extracted
    
    def smart_frame_filter(self, frames, similarity_threshold=0.85):
        """
        Filter out similar frames to reduce analysis costs
        Keep only frames where UI has significantly changed
        """
        if len(frames) <= 5:
            return frames
            
        filtered_frames = [frames[0]]  # Always keep first frame
        
        for i in range(1, len(frames)):
            # Simple similarity check based on file size (rough approximation)
            current_size = os.path.getsize(frames[i]["path"])
            last_size = os.path.getsize(filtered_frames[-1]["path"])
            
            size_diff = abs(current_size - last_size) / max(current_size, last_size)
            
            # If significant difference, keep the frame
            if size_diff > (1 - similarity_threshold):
                filtered_frames.append(frames[i])
                
        print(f"🔍 Filtered {len(frames)} → {len(filtered_frames)} unique frames")
        return filtered_frames
    
    def encode_image_for_openai(self, image_path):
        """Encode image to base64 for OpenAI API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def create_analysis_payload(self, frames, test_description="LegalCopilot QA Test"):
        """
        Create OpenAI API payload for frame analysis
        """
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze these screenshots from a QA test video of LegalCopilot PDF converter.
                            
Test Description: {test_description}

Please identify:
1. UI/UX Issues: Buttons not working, layout problems, misaligned elements
2. Functional Issues: Errors, crashes, loading problems, stuck processes  
3. User Experience: Confusing workflows, poor feedback, accessibility issues
4. Visual Bugs: Overlapping text, missing content, rendering problems

For each issue found, provide:
- Frame timestamp where issue occurs
- Severity (High/Medium/Low)  
- Description of the problem
- Suggested fix

Format as structured analysis with clear sections."""
                        }
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.encode_image_for_openai(frame['path'])}",
                                "detail": "high"
                            }
                        } for frame in frames
                    ]
                }
            ],
            "max_tokens": 1500
        }
        
        return payload
    
    def process_qa_video(self, video_path, test_description="", fps_extract=0.5, max_frames=10):
        """
        Complete processing pipeline:
        1. Extract frames from video
        2. Filter similar frames  
        3. Create OpenAI analysis payload
        4. Save results
        """
        try:
            # Extract frames
            frames = self.extract_frames(video_path, fps_extract, max_frames)
            
            # Filter similar frames
            filtered_frames = self.smart_frame_filter(frames)
            
            # Create analysis payload
            payload = self.create_analysis_payload(filtered_frames, test_description)
            
            # Save payload for manual API call
            video_name = Path(video_path).stem
            payload_path = self.frames_folder / f"{video_name}_analysis_payload.json"
            
            with open(payload_path, 'w') as f:
                # Don't save the base64 images in JSON (too large)
                summary_payload = payload.copy()
                summary_payload["messages"][0]["content"] = [
                    summary_payload["messages"][0]["content"][0],
                    {"type": "text", "text": f"[{len(filtered_frames)} images attached]"}
                ]
                json.dump(summary_payload, f, indent=2)
            
            print(f"\n📋 QA Analysis Summary:")
            print(f"Video: {video_path}")
            print(f"Frames extracted: {len(frames)}")
            print(f"Frames for analysis: {len(filtered_frames)}")
            print(f"Estimated cost: ${len(filtered_frames) * 0.01:.2f}")
            print(f"Payload saved: {payload_path}")
            
            return {
                "video_path": str(video_path),
                "frames_extracted": len(frames),
                "frames_analyzed": len(filtered_frames),
                "estimated_cost": len(filtered_frames) * 0.01,
                "payload_path": str(payload_path),
                "frames": filtered_frames
            }
            
        except Exception as e:
            print(f"❌ Error processing video: {e}")
            return None

def main():
    """Process QA videos in the QA folder"""
    extractor = VideoQAExtractor()
    qa_folder = Path("QA")
    
    # Find video files
    video_files = list(qa_folder.glob("**/*.mkv")) + list(qa_folder.glob("**/*.mp4"))
    
    if not video_files:
        print("❌ No video files found in QA folder")
        return
    
    for video_file in video_files:
        print(f"\n🎬 Processing: {video_file.name}")
        result = extractor.process_qa_video(
            video_file, 
            test_description=f"Testing {video_file.stem}",
            fps_extract=0.5,  # 1 frame every 2 seconds (perfect for 20s videos)
            max_frames=10     # Max 10 frames = $0.10 cost
        )
        
        if result:
            print(f"✅ Processed successfully - Cost: ${result['estimated_cost']:.2f}")

if __name__ == "__main__":
    main()