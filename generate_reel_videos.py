"""
Script to generate 8 high-quality, 30-second topic-specific MP4 video reels
with real synthesized audio voiceovers, animated code typing, IDE terminal execution,
and synchronized subtitle overlays.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import win32com.client

VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Video Specs (9:16 vertical smartphone reel format: 540 x 960)
WIDTH = 540
HEIGHT = 960
FPS = 24
DURATION_SEC = 30
TOTAL_FRAMES = FPS * DURATION_SEC

def get_font(size: int, bold: bool = False):
    try:
        font_path = "C:/Windows/Fonts/consola.ttf" if not bold else "C:/Windows/Fonts/consolab.ttf"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

REEL_CONFIGS = [
    {
        "id": "REEL_001",
        "title": "Java Developer Debugging at 2 AM",
        "category": "Java",
        "color": (239, 68, 68), # Red
        "speech_text": (
            "It is 2 AM and my production Java code just threw a NullPointerException right before release. "
            "Why is the user object null? The user was initialized three functions ago! "
            "Instead of risky raw method calls, let us refactor this code using Java's Optional API "
            "and defensive null checks. Now the build succeeds and our microservice is completely protected."
        ),
        "code_lines": [
            "// UserService.java - 02:14 AM",
            "public class UserService {",
            "    public String getUserName(String id) {",
            "        User user = repository.findById(id);",
            "        return user.getName(); // CRASH!",
            "    }",
            "}",
            "",
            "// Terminal Output: NullPointerException",
            "// Refactoring with Defensive Optional:",
            "public String getSafeUserName(String id) {",
            "    return Optional.ofNullable(user)",
            "        .map(User::getName)",
            "        .orElse(\"Guest User\");",
            "}",
            "// [SUCCESS] Build completed in 1.2s",
            "// [STATUS] 0 Exceptions in Production"
        ],
        "captions": [
            (0, 8, "It is 2 AM and my production code just threw a NullPointerException..."),
            (8, 18, "Why is user null? Refactoring with Java Optional and defensive null checks."),
            (18, 30, "Now the build succeeds and our service is safe from runtime crashes!")
        ]
    },
    {
        "id": "REEL_002",
        "title": "Day in the Life of a FAANG SWE",
        "category": "Career",
        "color": (59, 130, 246), # Blue
        "speech_text": (
            "Welcome to a day in the life of a FAANG software engineer. "
            "Our morning starts with an architecture standup, reviewing pull requests, and diagnosing microservices latency. "
            "Software engineering is thirty percent writing code and seventy percent systems thinking. "
            "Today we are designing high throughput Kafka event streams handling eight hundred and fifty thousand messages per second."
        ),
        "code_lines": [
            "// 10:00 AM - Architecture Standup",
            "// 11:30 AM - Code Review: PR #1842",
            "git checkout -b feat/kafka-event-stream",
            "",
            "// Distributed System Health Monitor",
            "Kafka Cluster: 12 Brokers Online",
            "Throughput: 850,000 msg/sec",
            "p99 Latency: 12ms (Target < 20ms)",
            "Active Microservices: 48 Services",
            "",
            "// High-Level Architecture Design",
            "Event-Driven Microservices with Redis Cache",
            "Zero Data Loss Idempotent Consumers",
            "// All services operating normally"
        ],
        "captions": [
            (0, 8, "Welcome to a day in the life of a FAANG software engineer."),
            (8, 18, "Software engineering is 30% typing and 70% distributed systems thinking."),
            (18, 30, "Monitoring microservices handling 850,000 messages per second with zero data loss.")
        ]
    },
    {
        "id": "REEL_003",
        "title": "Coding Interview: LeetCode Hard",
        "category": "DSA",
        "color": (168, 85, 247), # Purple
        "speech_text": (
            "Welcome to the technical coding interview reality check. "
            "The interviewer asked me to find the shortest path in a grid while inverting a binary tree in linear space. "
            "Instead of brute force, we model this as a breadth-first search traversal with optimal state pruning. "
            "Notice how our state queue guarantees O of V plus E optimal time complexity."
        ),
        "code_lines": [
            "// Interview Problem: Shortest Path in O(1) Extra Space",
            "class Solution {",
            "    public int shortestPath(int[][] grid, int k) {",
            "        int m = grid.length, n = grid[0].length;",
            "        Queue<int[]> queue = new ArrayDeque<>();",
            "        queue.offer(new int[]{0, 0, k});",
            "        boolean[][][] visited = new boolean[m][n][k+1];",
            "        ",
            "        // State Traversal: BFS Level Order",
            "        while (!queue.isEmpty()) {",
            "            int[] curr = queue.poll();",
            "            if (curr[0] == m-1 && curr[1] == n-1) return steps;",
            "        }",
            "        return -1; // Time: O(M*N*K), Space: O(M*N*K)",
            "    }",
            "}"
        ],
        "captions": [
            (0, 8, "Interviewer: Find shortest path while inverting a binary tree..."),
            (8, 18, "Instead of brute force, we model this as a Breadth-First Search traversal."),
            (18, 30, "Optimal state pruning guarantees clean O(V+E) time complexity.")
        ]
    },
    {
        "id": "REEL_004",
        "title": "M3 Max vs ThinkPad: Dev Benchmarks",
        "category": "Hardware",
        "color": (234, 179, 8), # Amber
        "speech_text": (
            "Today we are benchmarking the M3 Max MacBook Pro against the ThinkPad for heavy software engineering workflows. "
            "We tested Chromium compilation and running twelve Docker containers side by side. "
            "The unified memory bandwidth of four hundred gigabytes per second gives Apple Silicon a massive compile speed advantage."
        ),
        "code_lines": [
            "// Developer Compilation & Container Benchmarks",
            "Test Suite: Full Chromium Build (12 Docker Containers)",
            "",
            "1. Apple M3 Max (128GB Unified RAM):",
            "   Build Time: 3 min 12 sec",
            "   [████████████████████] 100% Speed",
            "   Memory Bandwidth: 400 GB/s",
            "",
            "2. ThinkPad P1 Gen 6 (Linux Ubuntu):",
            "   Build Time: 4 min 45 sec",
            "   [██████████████       ] 72% Speed",
            "   Raw Container Virtualization Lead",
            "",
            "// Verdict: High memory bandwidth accelerates builds by 38%"
        ],
        "captions": [
            (0, 8, "Compiling Chromium & running 12 Docker containers side-by-side."),
            (8, 18, "Testing memory bandwidth and local LLM inference speeds."),
            (18, 30, "400 GB/s unified memory bandwidth gives Apple Silicon a massive lead.")
        ]
    },
    {
        "id": "REEL_005",
        "title": "OpenAI & Anthropic New Dev APIs",
        "category": "AI",
        "color": (16, 185, 129), # Emerald
        "speech_text": (
            "OpenAI and Anthropic have released powerful new developer APIs that are fundamentally transforming software engineering. "
            "With native structured JSON schema guarantees and automated tool calling loops, developers are no longer just writing static logic. "
            "We are orchestrating intelligent agentic pipelines with ninety-eight percent automated test coverage."
        ),
        "code_lines": [
            "# Structured Outputs & Agentic Workflows",
            "from openai import OpenAI",
            "from pydantic import BaseModel",
            "",
            "class CodePipelineSchema(BaseModel):",
            "    topic: str",
            "    confidence: float",
            "    actions: list[str]",
            "",
            "client = OpenAI()",
            "response = client.beta.chat.completions.parse(",
            "    model=\"gpt-4o-mini\",",
            "    messages=[{\"role\": \"user\", \"content\": prompt}],",
            "    response_format=CodePipelineSchema",
            ")",
            "# Strict JSON Schema Guarantee: 100% Validated"
        ],
        "captions": [
            (0, 8, "New developer APIs bring native structured JSON schema guarantees."),
            (8, 18, "Engineers are now orchestrating agentic pipelines and tool loops."),
            (18, 30, "Building production AI systems with strict type safety and schema validation.")
        ]
    },
    {
        "id": "REEL_006",
        "title": "How Binary Search ACTUALLY Works",
        "category": "DSA",
        "color": (6, 182, 212), # Cyan
        "speech_text": (
            "Did you know that standard binary search implementations in Java and C++ have a hidden integer overflow bug? "
            "When low and high indices are very large numbers, low plus high overflows into negative integers. "
            "To write safe, production-grade algorithms, always compute mid as low plus high minus low divided by two."
        ),
        "code_lines": [
            "// The Classic Integer Overflow Bug in Java/C++",
            "int low = 1_000_000_000;",
            "int high = 1_500_000_000;",
            "",
            "// BUGGY ARITHMETIC:",
            "int mid = (low + high) / 2;",
            "// 2,500,000,000 > Integer.MAX_VALUE!",
            "// Result overflows to: -897,483,648 (CRASH)",
            "",
            "// SAFE PRODUCTION CODE:",
            "int mid = low + (high - low) / 2; // SAFE!",
            "",
            "// Bitwise Unsigned Shift:",
            "int mid = (low + high) >>> 1; // 100% Safe"
        ],
        "captions": [
            (0, 8, "Why mid = (low + high) / 2 has an integer overflow bug in Java and C++!"),
            (8, 18, "When low and high are large, their sum overflows into negative numbers."),
            (18, 30, "Always use low + (high - low) / 2 for memory and pointer safety.")
        ]
    },
    {
        "id": "REEL_007",
        "title": "Minimalist Dev & Gaming Setup",
        "category": "Gaming",
        "color": (236, 72, 153), # Pink
        "speech_text": (
            "Here is a tour of my minimalist dual-boot workstation, engineered for both high-productivity programming and competitive gaming. "
            "We use a Thunderbolt 4 KVM switcher to seamlessly alternate between a MacBook Pro for development and an RTX 4090 rig for gaming at 240 Hertz. "
            "Ergonomic split keyboards and studio audio ensure maximum comfort during long coding sessions."
        ),
        "code_lines": [
            "// Workstation Configuration & Ergonomics",
            "Primary Display: 32\" 4K 144Hz IPS (Code & Architecture)",
            "Secondary Display: 27\" OLED 240Hz (Gaming / Simulation)",
            "",
            "// Thunderbolt 4 KVM Dual-Boot Switch:",
            "Mode A: MacBook Pro M3 Max (Dev Workflow)",
            "Mode B: RTX 4090 Custom Rig (Gaming & AI Training)",
            "",
            "Split Ergonomic Keyboard: 62g Zealio Switches",
            "Audio: Studio Monitors + Shure SM7B Voice Mic",
            "Status: 240 FPS Constant | Thermals: 44°C Quiet"
        ],
        "captions": [
            (0, 8, "Dual-boot workstation setup for 4K coding and high-FPS gaming."),
            (8, 18, "Thunderbolt KVM switching with custom IDE macro keypads."),
            (18, 30, "Clean cable management and split ergonomics for long development sessions.")
        ]
    },
    {
        "id": "REEL_008",
        "title": "The $100M Cloud Outage Autopsy",
        "category": "Cloud",
        "color": (249, 115, 22), # Orange
        "speech_text": (
            "Today we dissect the one hundred million dollar cloud outage incident. "
            "A routine BGP route configuration update leaked into the public internet, misrouting forty percent of global ingress traffic. "
            "This triggered a cascading split-brain syndrome across distributed data centers. "
            "Learn why resilient circuit breakers and canary rollouts are critical for modern cloud infrastructure."
        ),
        "code_lines": [
            "// Incident Postmortem: Global Outage #88921",
            "Root Cause: BGP Route Leak & DNS Cascade",
            "",
            "Incident Timeline:",
            "14:02:10 - BGP configuration update pushed to production",
            "14:02:45 - 40% of global ingress traffic misrouted",
            "14:04:12 - Distributed split-brain in Region US-EAST",
            "14:08:30 - Automated circuit breaker triggered safe failover",
            "",
            "// Reliability Engineering Mitigation:",
            "Automated Canary Validation & Safe Rollback Pipelines"
        ],
        "captions": [
            (0, 8, "How a single BGP misconfiguration took down 40% of global traffic."),
            (8, 18, "Dissecting distributed failovers, split-brain, and cascading outages."),
            (18, 30, "Why resilience engineering and circuit breakers matter in cloud systems.")
        ]
    }
]

def generate_voiceover_audio(speech_text: str, output_wav_path: str):
    """Synthesizes speech into a crystal-clear WAV audio file using Windows SAPI5."""
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        stream = win32com.client.Dispatch("SAPI.SpFileStream")
        # 3 = SSFMCreateForWrite
        stream.Open(output_wav_path, 3, False)
        speaker.AudioOutputStream = stream
        speaker.Rate = 0  # Normal conversational speaking speed
        speaker.Volume = 100
        speaker.Speak(speech_text)
        stream.Close()
        return True
    except Exception as e:
        print(f"Warning: Audio synthesis failed for {output_wav_path}: {e}")
        return False

def render_frame(config: dict, frame_num: int) -> np.ndarray:
    """Renders a single frame of vertical Reel video."""
    t_sec = frame_num / FPS
    progress = frame_num / TOTAL_FRAMES

    # 1. Base Image (Dark modern slate theme)
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font(21, bold=True)
    font_badge = get_font(14, bold=True)
    font_code = get_font(14, bold=False)
    font_caption = get_font(16, bold=True)
    font_meta = get_font(13, bold=False)

    # 2. Header Bar
    draw.rectangle([(0, 0), (WIDTH, 70)], fill=(30, 41, 59))
    cat_color = config.get("color", (59, 130, 246))
    draw.rounded_rectangle([(20, 20), (120, 50)], radius=6, fill=cat_color)
    draw.text((32, 26), config["category"].upper(), fill=(255, 255, 255), font=font_badge)
    timer_str = f"00:{int(t_sec):02d} / 00:{DURATION_SEC:02d}"
    draw.text((WIDTH - 140, 26), timer_str, fill=(148, 163, 184), font=font_meta)

    # 3. Title Box
    draw.text((20, 85), config["title"], fill=(248, 250, 252), font=font_title)

    # 4. Animated IDE / Terminal Window (Center Canvas)
    ide_top = 125
    ide_bottom = 745
    draw.rounded_rectangle([(16, ide_top), (WIDTH - 16, ide_bottom)], radius=12, fill=(2, 6, 23), outline=(51, 65, 85), width=2)
    # Window controls
    draw.ellipse([(32, ide_top + 14), (44, ide_top + 26)], fill=(239, 68, 68))
    draw.ellipse([(52, ide_top + 14), (64, ide_top + 26)], fill=(234, 179, 8))
    draw.ellipse([(72, ide_top + 14), (84, ide_top + 26)], fill=(34, 197, 94))
    draw.text((100, ide_top + 12), f"Terminal • {config['id']}.sh", fill=(100, 116, 139), font=font_meta)
    draw.line([(16, ide_top + 40), (WIDTH - 16, ide_top + 40)], fill=(30, 41, 59), width=1)

    # Animated Code Typing Line by Line
    code_lines = config["code_lines"]
    total_lines = len(code_lines)
    visible_lines_count = min(int((t_sec / (DURATION_SEC * 0.90)) * total_lines) + 1, total_lines)

    curr_y = ide_top + 50
    for i in range(visible_lines_count):
        line = code_lines[i]
        line_color = (226, 232, 240)
        if line.startswith("//") or line.startswith("#"):
            line_color = (100, 116, 139)
        elif "ERROR" in line or "BUGGY" in line or "CRASH" in line or "Overflow" in line:
            line_color = (248, 113, 113)
        elif "SUCCESS" in line or "SAFE" in line or "CORRECT" in line or "Online" in line or "STATUS" in line:
            line_color = (74, 222, 128)
        elif "public" in line or "class" in line or "return" in line or "import" in line or "def" in line:
            line_color = (96, 165, 250)

        draw.text((26, curr_y), f"{i+1:2d}", fill=(71, 85, 105), font=font_code)
        draw.text((54, curr_y), line, fill=line_color, font=font_code)
        curr_y += 24

    # Blinking cursor
    if int(t_sec * 2) % 2 == 0 and curr_y < ide_bottom - 20:
        draw.rectangle([(54, curr_y), (64, curr_y + 16)], fill=(56, 189, 248))

    # 5. Live Audio Subtitles & Voiceover Box (Bottom Overlay)
    caption_text = ""
    for start, end, cap in config["captions"]:
        if start <= t_sec <= end:
            caption_text = cap
            break
    if not caption_text and config["captions"]:
        caption_text = config["captions"][-1][2]

    draw.rounded_rectangle([(16, 760), (WIDTH - 16, 885)], radius=10, fill=(30, 41, 59), outline=(71, 85, 105), width=1)
    draw.text((28, 770), "🔊 Live Voiceover & Subtitles:", fill=(148, 163, 184), font=font_meta)
    
    words = caption_text.split()
    line1 = " ".join(words[: len(words)//2 + 1])
    line2 = " ".join(words[len(words)//2 + 1:])
    draw.text((28, 796), f"\"{line1}\"", fill=(255, 255, 255), font=font_caption)
    if line2:
        draw.text((28, 826), f" {line2}\"", fill=(255, 255, 255), font=font_caption)

    # 6. Bottom Reel Progress Bar
    bar_y = HEIGHT - 12
    draw.rectangle([(0, bar_y), (WIDTH, HEIGHT)], fill=(30, 41, 59))
    draw.rectangle([(0, bar_y), (int(WIDTH * progress), HEIGHT)], fill=(37, 99, 235))

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def generate_all_reels():
    print(f"Generating 8 Reel MP4 videos and WAV audio voiceovers in {VIDEOS_DIR}...")
    for idx, cfg in enumerate(REEL_CONFIGS):
        video_out_path = os.path.join(VIDEOS_DIR, f"{cfg['id']}.mp4")
        audio_out_path = os.path.join(VIDEOS_DIR, f"{cfg['id']}.wav")
        safe_title = cfg['title'].encode('ascii', 'ignore').decode('ascii')

        # 1. Synthesize Spoken Voiceover Audio
        print(f"[{idx+1}/8] Synthesizing Voiceover Audio for {cfg['id']}: {safe_title}...")
        generate_voiceover_audio(cfg["speech_text"], audio_out_path)
        audio_size_kb = os.path.getsize(audio_out_path)/1024 if os.path.exists(audio_out_path) else 0

        # 2. Render 30-second Video (720 frames)
        print(f"[{idx+1}/8] Rendering Video for {cfg['id']} ({DURATION_SEC}s, {TOTAL_FRAMES} frames)...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_out_path, fourcc, FPS, (WIDTH, HEIGHT))
        
        for f in range(TOTAL_FRAMES):
            frame = render_frame(cfg, f)
            out.write(frame)
            
        out.release()
        vid_size_kb = os.path.getsize(video_out_path)/1024 if os.path.exists(video_out_path) else 0
        print(f"  -> Saved Video: {video_out_path} ({vid_size_kb:.1f} KB)")
        print(f"  -> Saved Audio: {audio_out_path} ({audio_size_kb:.1f} KB)")

    print("\nAll 8 Reel Videos & Audio Voiceovers generated successfully!")

if __name__ == "__main__":
    generate_all_reels()
