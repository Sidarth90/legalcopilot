#!/usr/bin/env python3
"""
Simple QA Video Frame Extractor
Converts QA videos to key frame images for direct analysis
No APIs, no costs - just extract frames for manual review
"""

import cv2
import os
from pathlib import Path
from datetime import datetime

class SimpleFrameExtractor:
    def __init__(self, qa_folder="QA"):
        self.qa_folder = Path(qa_folder)
        self.screenshots_folder = self.qa_folder / "screenshots"
        self.screenshots_folder.mkdir(exist_ok=True)
        
    def extract_key_frames(self, video_path, frames_per_video=8):
        """
        Extract evenly spaced key frames from video
        For 20s video with 8 frames = 1 frame every 2.5 seconds
        """
        print(f"Processing: {video_path.name}")
        
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"ERROR: Could not open video: {video_path}")
            return []
            
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"Video: {duration:.1f}s, {fps:.1f} FPS")
        
        # Calculate frame intervals
        frame_interval = total_frames // frames_per_video
        extracted_frames = []
        
        # Create folder for this video
        video_name = video_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = self.screenshots_folder / f"{video_name}_{timestamp}"
        output_folder.mkdir(exist_ok=True)
        
        for i in range(frames_per_video):
            frame_number = i * frame_interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            if not ret:
                break
                
            # Calculate timestamp
            timestamp_sec = frame_number / fps
            
            # Save frame as high-quality image
            frame_filename = f"frame_{i+1:02d}_at_{timestamp_sec:.1f}s.png"
            frame_path = output_folder / frame_filename
            
            # Save with high quality
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_PNG_COMPRESSION, 1])
            
            extracted_frames.append({
                "path": str(frame_path),
                "timestamp": timestamp_sec,
                "frame_number": i + 1
            })
            
            print(f"Frame {i+1}/{frames_per_video}: {timestamp_sec:.1f}s -> {frame_filename}")
            
        cap.release()
        print(f"SUCCESS: Saved {len(extracted_frames)} frames to: {output_folder}")
        
        # Create summary HTML for easy viewing
        self.create_summary_html(output_folder, video_name, extracted_frames, duration)
        
        return extracted_frames
    
    def create_summary_html(self, output_folder, video_name, frames, duration):
        """Create HTML summary for easy frame viewing"""
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>QA Analysis: {video_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .frame-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .frame-item {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .frame-item img {{ width: 100%; height: auto; border-radius: 4px; cursor: pointer; }}
        .frame-info {{ margin-top: 10px; font-size: 14px; color: #666; }}
        .notes {{ margin-top: 15px; padding: 10px; background: #f9f9f9; border-radius: 4px; min-height: 60px; }}
        .notes textarea {{ width: 100%; border: none; background: transparent; resize: vertical; font-family: inherit; }}
        .severity {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .high {{ background: #fee; color: #c53030; }}
        .medium {{ background: #fff3cd; color: #b45309; }}
        .low {{ background: #f0fff4; color: #38a169; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ QA Analysis: {video_name}</h1>
        <p><strong>Video Duration:</strong> {duration:.1f} seconds</p>
        <p><strong>Frames Extracted:</strong> {len(frames)}</p>
        <p><strong>Analysis Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <h3>📋 Quick Analysis Checklist:</h3>
        <ul>
            <li>✅ PDF Upload Working?</li>
            <li>✅ UI Elements Properly Aligned?</li>
            <li>✅ No Loading/Stuck Issues?</li>
            <li>✅ Text/Buttons Readable?</li>
            <li>✅ Expected Functionality Working?</li>
        </ul>
    </div>
    
    <div class="frame-grid">"""
        
        for frame in frames:
            filename = Path(frame["path"]).name
            html_content += f"""
        <div class="frame-item">
            <img src="{filename}" alt="Frame {frame['frame_number']}" onclick="window.open('{filename}', '_blank')">
            <div class="frame-info">
                <strong>Frame {frame['frame_number']}</strong> - {frame['timestamp']:.1f}s
            </div>
            <div class="notes">
                <strong>Issues Found:</strong><br>
                <textarea placeholder="Describe any issues you see in this frame...
• UI problems (buttons, layout, alignment)
• Functional issues (errors, crashes, loading)
• Visual bugs (text overlap, missing content)
• UX issues (confusing workflow, poor feedback)

Severity: High/Medium/Low" rows="4"></textarea>
            </div>
        </div>"""
        
        html_content += """
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: white; border-radius: 8px;">
        <h3>📝 Overall QA Summary</h3>
        <textarea style="width: 100%; height: 100px; border: 1px solid #ddd; border-radius: 4px; padding: 10px;" 
                  placeholder="Overall assessment of the QA test:
• What was being tested?
• Major issues found?
• Recommended fixes?
• Priority level for fixes?"></textarea>
    </div>
</body>
</html>"""
        
        summary_path = output_folder / "QA_Analysis.html"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Summary created: {summary_path}")

def main():
    extractor = SimpleFrameExtractor()
    qa_folder = Path("QA")
    
    # Find all video files
    video_extensions = ['*.mkv', '*.mp4', '*.avi', '*.mov']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(qa_folder.glob(f"**/{ext}"))
    
    if not video_files:
        print("ERROR: No video files found in QA folder")
        print(f"Looking in: {qa_folder.absolute()}")
        return
    
    print(f"Found {len(video_files)} video(s) to process")
    
    for video_file in video_files:
        print(f"\n" + "="*50)
        frames = extractor.extract_key_frames(video_file, frames_per_video=8)
        
        if frames:
            print(f"SUCCESS! Open QA_Analysis.html to review frames")
        
        print("="*50)

if __name__ == "__main__":
    main()