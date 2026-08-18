"""
Script to generate 8 high-quality, topic-specific MP4 video reels (15-25 seconds each)
with animated code typing, IDE terminal execution, benchmarks, and subtitle overlays.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

VIDEOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

# Video Specs (9:16 vertical smartphone reel format: 540 x 960)
WIDTH = 540
HEIGHT = 960
FPS = 24
DURATION_SEC = 20
TOTAL_FRAMES = FPS * DURATION_SEC

def get_font(size: int, bold: bool = False):
    try:
        # Common Windows fonts
        font_path = "C:/Windows/Fonts/consola.ttf" if not bold else "C:/Windows/Fonts/consolab.ttf"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

REEL_CONFIGS = [
    {
        "id": "REEL_001",
        "title": "Java Developer Debugging at 2 AM 😂",
        "category": "Java",
        "color": (239, 68, 68), # Red/Orange
        "code_lines": [
            "// UserService.java - 02:14 AM",
            "public class UserService {",
            "    public String getUserName(String id) {",
            "        User user = repository.findById(id);",
            "        return user.getName(); // CRASH!",
            "    }",
            "}",
            "",
            "// Terminal Output:",
            "ERROR: NullPointerException on line 5",
            "Fixing with Optional<User>...",
            "return Optional.ofNullable(user)",
            "    .map(User::getName)",
            "    .orElse(\"Guest\");",
            "// BUILD SUCCESSFUL in 1.4s"
        ],
        "captions": [
            (0, 5, "When NullPointerException hits right before deployment..."),
            (5, 12, "Line 482: How is user null? It's 2 AM and I'm debugging Java."),
            (12, 20, "Refactoring with Optional and defensive null checks!")
        ]
    },
    {
        "id": "REEL_002",
        "title": "Day in the Life of a FAANG SWE 💻☕",
        "category": "Career",
        "color": (59, 130, 246), # Blue
        "code_lines": [
            "// 10:00 AM - Architecture Standup",
            "// 11:30 AM - Code Review: PR #1842",
            "git checkout -b feat/kafka-microservices",
            "",
            "// System Health Monitor",
            "Kafka Cluster: 12 Brokers Online",
            "Throughput: 850,000 msg/sec",
            "p99 Latency: 14ms (Target < 20ms)",
            "Active Microservices: 48 Services",
            "",
            "// 02:00 PM - High-Level System Design",
            "Event Driven Architecture with Redis Cache",
            "Zero Data Loss Idempotent Consumers"
        ],
        "captions": [
            (0, 6, "Morning standup, code reviews, and distributed queue design."),
            (6, 13, "Software engineering is 30% typing and 70% system thinking."),
            (13, 20, "Monitoring microservices handling 850k requests per second.")
        ]
    },
    {
        "id": "REEL_003",
        "title": "Coding Interview: LeetCode Hard Reality 😭",
        "category": "DSA",
        "color": (168, 85, 247), # Purple
        "code_lines": [
            "// Interview Question: Shortest Path in O(1) Space",
            "// Candidate: \"Can I use Dijkstra with a Heap?\"",
            "",
            "class Solution {",
            "    public int shortestPath(int[][] grid) {",
            "        int m = grid.length, n = grid[0].length;",
            "        Queue<int[]> queue = new ArrayDeque<>();",
            "        queue.offer(new int[]{0, 0, 0});",
            "        // State: (row, col, obstacle_count)",
            "        // Time Complexity: O(V + E)",
            "        // Space Complexity: O(V)",
            "        return bfs(grid, queue);",
            "    }",
            "}"
        ],
        "captions": [
            (0, 6, "Interviewer: Invert a binary tree while detecting graph cycles..."),
            (6, 13, "Why does every tech interview feel like an Olympic math duel?"),
            (13, 20, "BFS shortest path traversal with optimal state pruning.")
        ]
    },
    {
        "id": "REEL_004",
        "title": "M3 Max vs ThinkPad: Dev Benchmarks 🔥",
        "category": "Hardware",
        "color": (234, 179, 8), # Amber
        "code_lines": [
            "// Workstation Compilation Benchmarks",
            "Test: Chromium Full Build (12 Containers)",
            "",
            "1. Apple M3 Max (128GB Unified Memory):",
            "   [████████████████████] 3 min 12 sec",
            "   Memory Bandwidth: 400 GB/s",
            "",
            "2. ThinkPad P1 Gen 6 (Linux Ubuntu):",
            "   [██████████████       ] 4 min 45 sec",
            "   Raw Container Virtualization Lead",
            "",
            "Verdict: M3 Max crushes local compile times!"
        ],
        "captions": [
            (0, 6, "Compiling Chromium & running 12 Docker containers side-by-side."),
            (6, 13, "Testing memory bandwidth and local LLM inference speeds."),
            (13, 20, "Unified memory bandwidth gives Apple Silicon a massive lead.")
        ]
    },
    {
        "id": "REEL_005",
        "title": "OpenAI & Anthropic New Dev APIs 🤖",
        "category": "AI",
        "color": (16, 185, 129), # Emerald
        "code_lines": [
            "# Structured Outputs & Agentic Workflows",
            "from openai import OpenAI",
            "client = OpenAI()",
            "",
            "response = client.beta.chat.completions.parse(",
            "    model=\"gpt-4o-mini\",",
            "    messages=[{\"role\": \"user\", \"content\": prompt}],",
            "    response_format=CodeAnalysisSchema",
            ")",
            "",
            "# Strict JSON Schema Guarantee: 100%",
            "event_loop.orchestrate_tools(response.tools)",
            "print(\"Automated Test Coverage: 98.4%\")"
        ],
        "captions": [
            (0, 6, "New developer APIs bring native structured JSON schema guarantees."),
            (6, 13, "Engineers are now orchestrating agentic pipelines and tool loops."),
            (13, 20, "Building production AI systems with strict output validation.")
        ]
    },
    {
        "id": "REEL_006",
        "title": "How Binary Search ACTUALLY Works 🧠",
        "category": "DSA",
        "color": (6, 182, 212), # Cyan
        "code_lines": [
            "// The Classic Integer Overflow Bug in Java/C++",
            "",
            "int low = 1_000_000_000;",
            "int high = 1_500_000_000;",
            "",
            "// BUGGY CODE:",
            "int mid = (low + high) / 2; // OVERFLOW! -> Negative",
            "",
            "// SAFE CODE:",
            "int mid = low + (high - low) / 2; // CORRECT!",
            "",
            "// Bitwise Alternative:",
            "int mid = (low + high) >>> 1; // Unsigned shift"
        ],
        "captions": [
            (0, 6, "Why mid = (low + high) / 2 has an integer overflow bug in Java/C++!"),
            (6, 13, "When low and high are large, their sum overflows into negative numbers."),
            (13, 20, "Always use low + (high - low) / 2 for pointer safety.")
        ]
    },
    {
        "id": "REEL_007",
        "title": "Minimalist Dev & Gaming Setup 🎮",
        "category": "Gaming",
        "color": (236, 72, 153), # Pink
        "code_lines": [
            "// Workstation Configuration",
            "Monitor 1: 32\" 4K 144Hz IPS (Code & Docs)",
            "Monitor 2: 27\" OLED 240Hz (Competitive Gaming)",
            "",
            "// Thunderbolt 4 KVM Switcher:",
            "Mode A: MacBook Pro M3 Max (Dev Workflow)",
            "Mode B: RTX 4090 Custom Rig (Gaming/Training)",
            "",
            "Custom Split Mechanical Keyboard: 62g Zealios",
            "Audio: Studio Monitors + Shure SM7B Mic",
            "FPS: 240 FPS Constant | Thermals: 48°C"
        ],
        "captions": [
            (0, 6, "Dual-boot workstation setup for 4K coding and high-FPS gaming."),
            (6, 13, "Thunderbolt KVM switching with custom IDE macro keypads."),
            (13, 20, "Clean cable management and split ergonomics for long sessions.")
        ]
    },
    {
        "id": "REEL_008",
        "title": "The $100M Cloud Outage Autopsy ☁️💥",
        "category": "Cloud",
        "color": (249, 115, 22), # Orange
        "code_lines": [
            "// Outage Postmortem: Incident #88921",
            "Root Cause: BGP Route Leak & DNS Cascade",
            "",
            "Timeline of Failure:",
            "14:02:10 - BGP configuration update pushed",
            "14:02:45 - 40% of global ingress traffic misrouted",
            "14:04:12 - Distributed split-brain in Region US-EAST",
            "14:08:30 - Circuit breaker triggered failover",
            "",
            "// Mitigation Strategy:",
            "Automated Canary Validation & Safe Rollbacks"
        ],
        "captions": [
            (0, 6, "How a single BGP misconfiguration took down 40% of traffic."),
            (6, 13, "Dissecting distributed failovers, split-brain, and cascading outages."),
            (13, 20, "Why resilience engineering and circuit breakers matter in cloud systems.")
        ]
    }
]

def render_frame(config: dict, frame_num: int) -> np.ndarray:
    """Renders a single frame of vertical Reel video."""
    t_sec = frame_num / FPS
    progress = frame_num / TOTAL_FRAMES

    # 1. Base Image (Dark modern theme)
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)

    # Fonts
    font_title = get_font(22, bold=True)
    font_badge = get_font(14, bold=True)
    font_code = get_font(15, bold=False)
    font_caption = get_font(16, bold=True)
    font_meta = get_font(13, bold=False)

    # 2. Header Bar
    draw.rectangle([(0, 0), (WIDTH, 70)], fill=(30, 41, 59))
    # Category badge
    cat_color = config.get("color", (59, 130, 246))
    draw.rounded_rectangle([(20, 20), (120, 50)], radius=6, fill=cat_color)
    draw.text((32, 26), config["category"].upper(), fill=(255, 255, 255), font=font_badge)
    # Timer
    timer_str = f"00:{int(t_sec):02d} / 00:{DURATION_SEC:02d}"
    draw.text((WIDTH - 140, 26), timer_str, fill=(148, 163, 184), font=font_meta)

    # 3. Title Box
    draw.text((20, 85), config["title"], fill=(248, 250, 252), font=font_title)

    # 4. Animated IDE / Terminal Window (Center Canvas)
    ide_top = 130
    ide_bottom = 750
    draw.rounded_rectangle([(16, ide_top), (WIDTH - 16, ide_bottom)], radius=12, fill=(2, 6, 23), outline=(51, 65, 85), width=2)
    # Window controls (red, yellow, green dots)
    draw.ellipse([(32, ide_top + 14), (44, ide_top + 26)], fill=(239, 68, 68))
    draw.ellipse([(52, ide_top + 14), (64, ide_top + 26)], fill=(234, 179, 8))
    draw.ellipse([(72, ide_top + 14), (84, ide_top + 26)], fill=(34, 197, 94))
    draw.text((100, ide_top + 12), f"Terminal • {config['id']}.sh", fill=(100, 116, 139), font=font_meta)
    draw.line([(16, ide_top + 40), (WIDTH - 16, ide_top + 40)], fill=(30, 41, 59), width=1)

    # Animated Code Typing Line by Line
    code_lines = config["code_lines"]
    total_lines = len(code_lines)
    visible_lines_count = min(int((t_sec / (DURATION_SEC * 0.85)) * total_lines) + 1, total_lines)

    curr_y = ide_top + 55
    for i in range(visible_lines_count):
        line = code_lines[i]
        line_color = (226, 232, 240)
        if line.startswith("//") or line.startswith("#"):
            line_color = (100, 116, 139) # Slate comment
        elif "ERROR" in line or "BUGGY" in line or "CRASH" in line:
            line_color = (248, 113, 113) # Red
        elif "SUCCESS" in line or "SAFE" in line or "CORRECT" in line or "Online" in line:
            line_color = (74, 222, 128) # Green
        elif "public" in line or "class" in line or "return" in line or "import" in line or "def" in line:
            line_color = (96, 165, 250) # Blue keyword

        # Line number
        draw.text((28, curr_y), f"{i+1:2d}", fill=(71, 85, 105), font=font_code)
        draw.text((58, curr_y), line, fill=line_color, font=font_code)
        curr_y += 26

    # Blinking cursor on active line
    if int(t_sec * 2) % 2 == 0 and curr_y < ide_bottom - 20:
        draw.rectangle([(58, curr_y), (68, curr_y + 18)], fill=(56, 189, 248))

    # 5. Live Audio Subtitles / Captions (Bottom Overlay)
    caption_text = ""
    for start, end, cap in config["captions"]:
        if start <= t_sec <= end:
            caption_text = cap
            break
    if not caption_text and config["captions"]:
        caption_text = config["captions"][-1][2]

    draw.rounded_rectangle([(16, 765), (WIDTH - 16, 885)], radius=10, fill=(30, 41, 59, 240), outline=(71, 85, 105), width=1)
    draw.text((28, 775), "🔊 Subtitles & Audio Voiceover:", fill=(148, 163, 184), font=font_meta)
    
    # Wrap caption text into 2 lines if needed
    words = caption_text.split()
    line1 = " ".join(words[: len(words)//2 + 1])
    line2 = " ".join(words[len(words)//2 + 1:])
    draw.text((28, 800), f"\"{line1}\"", fill=(255, 255, 255), font=font_caption)
    if line2:
        draw.text((28, 830), f" {line2}\"", fill=(255, 255, 255), font=font_caption)

    # 6. Bottom Reel Progress Bar
    bar_y = HEIGHT - 12
    draw.rectangle([(0, bar_y), (WIDTH, HEIGHT)], fill=(30, 41, 59))
    draw.rectangle([(0, bar_y), (int(WIDTH * progress), HEIGHT)], fill=(37, 99, 235))

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def generate_all_videos():
    print(f"Generating 8 Reel MP4 videos in {VIDEOS_DIR}...")
    for idx, cfg in enumerate(REEL_CONFIGS):
        out_path = os.path.join(VIDEOS_DIR, f"{cfg['id']}.mp4")
        safe_title = cfg['title'].encode('ascii', 'ignore').decode('ascii')
        print(f"Rendering [{idx+1}/8] {cfg['id']}: {safe_title} ({DURATION_SEC}s, {TOTAL_FRAMES} frames)...")
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(out_path, fourcc, FPS, (WIDTH, HEIGHT))
        
        for f in range(TOTAL_FRAMES):
            frame = render_frame(cfg, f)
            out.write(frame)
            
        out.release()
        size_kb = os.path.getsize(out_path)/1024 if os.path.exists(out_path) else 0
        print(f"  -> Saved: {out_path} ({size_kb:.1f} KB)")

    print("\nAll 8 Reel MP4 videos generated successfully!")

if __name__ == "__main__":
    generate_all_videos()
