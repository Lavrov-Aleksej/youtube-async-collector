import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from datetime import datetime
from controllers.youtube_api_controller import YouTubeDataParser

from calendar import monthrange

class YouTubeAsyncApp:
    def __init__(self, root):
        """Initialization of the asynchronous application for working with YouTube API"""
        self.root = root
        self.root.title("YouTube Data Collector (Asynchronous)")
        self.root.geometry("900x700")

        # Create a separate event loop for asynchronous operations
        self.loop = asyncio.new_event_loop()
        # Start the loop in a separate thread
        self.thread = Thread(target=self.start_loop, args=(self.loop,), daemon=True)
        self.thread.start()

        self.api_key = None  # YouTube API key
        self.con = None  # Controller for working with YouTube API

        self.list_videos_id = None

        # Create a dialog for API key input
        self.create_api_key_dialog()

    def start_loop(self, loop):
        """Start the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def run_async(self, coro, operation_name=None):
        """Run asynchronous functions and handle their results"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.operation_name = operation_name  # Save the operation name
        future.add_done_callback(self.handle_async_result)
        return future

    def handle_async_result(self, future):
        """Handle results of asynchronous operations"""
        try:
            result = future.result()
            # Check the operation name if it was set
            if hasattr(future, 'operation_name') and future.operation_name == "search_videos":
                pass
            elif result is not None:
                self.log_message(f"Operation completed: {str(result)}")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))

    def create_api_key_dialog(self):
        """Create a dialog window for API key input"""
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("API Key Required")
        self.dialog.geometry("450x180")
        self.center_window(self.dialog)
        
        ttk.Label(self.dialog, text="Enter your YouTube Data API key:").pack(pady=(10, 5))
    
        self.api_key_entry = ttk.Entry(self.dialog, width=50)
        self.api_key_entry.pack(pady=5)
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="OK", command=self.validate_and_connect).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.root.destroy).pack(side=tk.LEFT, padx=10)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.dialog.grab_set()  # Make the window modal

    def validate_and_connect(self):
        """Validate API key and establish connection"""
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "API key cannot be empty")
            return

        # Key format validation
        if not (api_key.startswith('AIza') and len(api_key) > 30):
            if not messagebox.askyesno("Confirmation", 
                                    "Non-standard YouTube API key format. Continue?"):
                return

        self.api_key = api_key
        try:
            # Initialize YouTube API controller
            self.con = YouTubeDataParser(api_key=self.api_key)  
            messagebox.showinfo("Success", "API connection established successfully")
            self.dialog.destroy()
            self.create_main_interface()  # Create main interface
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to establish connection: {str(e)}")
            self.con = None

    def center_window(self, window, offset_x=350):
        """Center the window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() - width) // 2 + offset_x 
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def create_main_interface(self):
        """Create the main application interface"""
        # Search parameters frame
        search_frame = ttk.LabelFrame(self.root, text="Search Parameters", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=10, anchor='nw')
        
        # Left side - video search parameters
        ttk.Label(search_frame, text="Search query:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.query_entry = ttk.Entry(search_frame, width=40)
        self.query_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        self.query_entry.insert(0, "Евгения Потапова")
        
        ttk.Label(search_frame, text="Max count:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_results_entry = ttk.Entry(search_frame, width=10)
        self.max_results_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        self.max_results_entry.insert(0, "42")
        
        ttk.Label(search_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.category_entry = ttk.Entry(search_frame, width=10)
        self.category_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        self.category_entry.insert(0, "1")

        # Separator
        ttk.Separator(search_frame, orient=tk.VERTICAL).grid(row=0, column=2, rowspan=3, sticky='ns', padx=10)

        # Right side - specific video parameters
        ttk.Label(search_frame, text="Video ID | URL:").grid(row=0, column=3, sticky=tk.W, padx=10, pady=2)
        self.url_videos = ttk.Entry(search_frame, width=40)
        self.url_videos.grid(row=0, column=4, padx=5, pady=2, sticky=tk.W)
        self.url_videos.insert(0, "TZlivmpK2n4")
        
        ttk.Label(search_frame, text="Start date (YYYY-MM-DD):").grid(row=1, column=3, sticky=tk.W, padx=10, pady=2)
        self.date_after_entry = ttk.Entry(search_frame, width=15)
        self.date_after_entry.grid(row=1, column=4, padx=5, pady=2, sticky=tk.W)
        self.date_after_entry.insert(0, "2005-02-14")

        ttk.Label(search_frame, text="End date (YYYY-MM-DD):").grid(row=2, column=3, sticky=tk.W, padx=10, pady=2)
        self.date_before_entry = ttk.Entry(search_frame, width=15)
        self.date_before_entry.grid(row=2, column=4, padx=5, pady=2, sticky=tk.W)
        self.date_before_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Quick search frame
        fast_search_frame = ttk.LabelFrame(self.root, text="Quick Search", padding=10)
        fast_search_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, anchor='nw')
        
        # Create frame for the first row (year and buttons)
        year_row_frame = ttk.Frame(fast_search_frame)
        year_row_frame.pack(fill=tk.X, pady=2)

        # Year input field
        ttk.Label(year_row_frame, text='Year (YYYY):').pack(side=tk.LEFT)
        self.fast_year = ttk.Entry(year_row_frame, width=15)
        self.fast_year.pack(side=tk.LEFT, padx=5)
        self.fast_year.insert(0, datetime.now().strftime("%Y"))

        # Function to set quarter
        def set_quarter(start_month, end_month):
            """Set dates for the selected quarter"""
            try:
                year = self.fast_year.get()
                if not year.isdigit() or len(year) != 4:
                    raise ValueError("Year must be in YYYY format")
                
                self.date_after_entry.delete(0, tk.END)
                self.date_after_entry.insert(0, f"{year}-{start_month:02d}-01")
                
                self.date_before_entry.delete(0, tk.END)
                self.date_before_entry.insert(0, f"{year}-{end_month:02d}-{monthrange(int(year), end_month)[1]}")
                self.log_message(f"Quarter for {year} selected")
            except Exception as e:
                self.log_message(f"Error: {str(e)}")

        # Quarter buttons
        ttk.Button(year_row_frame, text='Q1', 
                command=lambda: set_quarter(1, 3)).pack(side=tk.LEFT, padx=2)
        ttk.Button(year_row_frame, text='Q2', 
                command=lambda: set_quarter(4, 6)).pack(side=tk.LEFT, padx=2)
        ttk.Button(year_row_frame, text='Q3', 
                command=lambda: set_quarter(7, 9)).pack(side=tk.LEFT, padx=2)
        ttk.Button(year_row_frame, text='Q4', 
                command=lambda: set_quarter(10, 12)).pack(side=tk.LEFT, padx=2)

        # Control panel
        control_frame = ttk.LabelFrame(self.root, text="Control Panel", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5, anchor='nw')

        ttk.Button(control_frame, text="Search Videos", 
                command=lambda: self.run_async(self.search_videos(), operation_name="search_videos")).pack(side=tk.LEFT, padx=5)
           
        ttk.Button(control_frame, text="Process Videos", 
                 command=lambda: self.run_async(self.process_all_videos())).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text='Process Video by ID | URL', 
                 command=lambda: self.run_async(self.process_video_by_id())).pack(side=tk.LEFT, padx=5)

        # Operation log
        self.log_frame = ttk.LabelFrame(self.root, text="Operation Log", padding=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, anchor='nw')
                
        self.log_text = tk.Text(self.log_frame, wrap=tk.WORD, state='normal')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def log_message(self, message):
        """Add message to the log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)  
        self.root.update() 

    async def search_videos(self):
        """Asynchronous video search by specified parameters"""
        try:
            query = self.query_entry.get()
            max_results = int(self.max_results_entry.get())
            category = self.category_entry.get()
            date_after = self.date_after_entry.get()
            date_before = self.date_before_entry.get()

            self.log_message(f"Starting video search for query: {query}")

            self.list_videos_id = await self.con.search_videos(
                query=query,
                max_results=max_results,
                category=category,
                date_after=date_after,
                date_before=date_before
            )

            # Display only the count of found videos
            count = len(self.list_videos_id) if self.list_videos_id is not None else 0
            self.log_message(f"Videos found: {count}")
            return self.list_videos_id
        except Exception as e:
            self.log_message(f"Error during video search: {str(e)}")
            raise

    async def process_all_videos(self):
        """Asynchronous video processing with immediate ID logging after processing"""
        if not self.list_videos_id:
            self.log_message("No video list to process. Perform search first.")
            return 0

        self.log_message("Starting processing of all videos...")
        
        async def process_and_log(video_id):
            try:
                self.log_message(f"Currently processing video with ID: {video_id}")
                result = await self.con.create_data_video(video_id=video_id)
                outcome_message = (
                    f"Video {video_id} processed successfully"
                    if result
                    else f"Error processing video {video_id}"
                )
                self.log_message(outcome_message)
                return result
            except Exception as e:
                self.log_message(f"Error processing video {video_id}: {str(e)}")
                return False

        tasks = [process_and_log(video_id) for video_id in self.list_videos_id]
        results = await asyncio.gather(*tasks)

        success_count = sum(1 for r in results if r)
        self.log_message(f"Final result: processed {success_count} out of {len(self.list_videos_id)} videos")
        
        return success_count
    
    async def process_video_by_id(self):
        """Asynchronous processing of a specific video by ID"""
        try:
            video_id = self.url_videos.get().strip()
            self.log_message(f"Starting processing of video with ID: {video_id}")
            result = await self.con.create_data_video(video_id=video_id)
            self.log_message(f"Video {video_id} processing completed")
            return result
        except Exception as e:
            self.log_message(f"Error processing video: {str(e)}")
            raise

# Application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeAsyncApp(root)
    root.mainloop()