
import threading
import time
import os
import queue


class AIClusterOS:
    def __init__(self, total_ram_gb, num_gpus):
        # System resources
        self.total_ram_gb = total_ram_gb
        self.available_ram_gb = total_ram_gb
        self.ram_lock = threading.Lock()

        self.gpu_locks = {
            i: threading.Lock() for i in range(num_gpus)
        }
        self.gpu_status = {
            i: "IDLE" for i in range(num_gpus)
        }

        # Job queue and system state
        self.job_queue = queue.Queue()
        self.active_jobs = []
        self.active_jobs_lock = threading.Lock()
        self.is_running = True

        # Start dashboard and scheduler threads
        self.dash_thread = threading.Thread(
            target=self._dashboard_loop,
            daemon=True
        )
        self.dash_thread.start()

        self.scheduler_thread = threading.Thread(
            target=self._os_scheduler_loop
        )
        self.scheduler_thread.start()

    def _dashboard_loop(self):
        """Display current RAM, GPU, and job queue status."""
        while self.is_running:
            time.sleep(1.5)

            with self.ram_lock:
                available_ram = self.available_ram_gb

            with self.active_jobs_lock:
                active_count = len(self.active_jobs)

            print("\n" + "=" * 50)
            print(
                f"[LIVE DASHBOARD] RAM Available: "
                f"{available_ram}/{self.total_ram_gb} GB"
            )

            gpu_str = " | ".join(
                [f"GPU {i}: {self.gpu_status[i]}"
                 for i in self.gpu_locks]
            )
            print(f"[LIVE DASHBOARD] {gpu_str}")
            print(
                f"[LIVE DASHBOARD] Queue Size: "
                f"{self.job_queue.qsize()} | "
                f"Active Jobs: {active_count}"
            )
            print("=" * 50 + "\n")

    def submit_job(self, job_name, dataset_path,
                   req_ram, req_gpus, duration):
        """Add a job to the OS queue."""
        self.job_queue.put(
            (job_name, dataset_path, req_ram, req_gpus, duration)
        )
        print(f"[API] Submitted: {job_name} -> Queued.")

    def _os_scheduler_loop(self):
        """Get jobs from the queue and start worker threads."""
        while self.is_running or not self.job_queue.empty():
            try:
                job_data = self.job_queue.get(timeout=1)
                worker = threading.Thread(
                    target=self._execute_job,
                    args=job_data
                )
                worker.start()
            except queue.Empty:
                continue

    def _execute_job(self, job_name, dataset_path,
                     req_ram, req_gpus, duration):
        """Manage the resources needed by one job."""
        allocated_ram = False
        acquired_gpus = []

        try:
            # File system check
            if not os.path.exists(dataset_path):
                print(
                    f"[{job_name}] FAILED: Dataset "
                    f"'{dataset_path}' not found or permission denied."
                )
                return

            with self.active_jobs_lock:
                self.active_jobs.append(job_name)

            # Memory management
            print(f"[{job_name}] Waiting for {req_ram}GB RAM...")

            if req_ram > self.total_ram_gb:
                print(f"[{job_name}] FAILED: Not enough total RAM.")
                return

            while True:
                with self.ram_lock:
                    if self.available_ram_gb >= req_ram:
                        self.available_ram_gb -= req_ram
                        allocated_ram = True
                        break
                time.sleep(0.5)

            print(f"[{job_name}] Allocated {req_ram}GB RAM.")

            # Deadlock avoidance: acquire GPUs in sorted order
            sorted_gpus = sorted(req_gpus)

            for gpu in sorted_gpus:
                if gpu not in self.gpu_locks:
                    print(f"[{job_name}] FAILED: GPU {gpu} does not exist.")
                    return

            if sorted_gpus:
                print(f"[{job_name}] Waiting for GPUs {sorted_gpus}...")

            for gpu in sorted_gpus:
                self.gpu_locks[gpu].acquire()
                acquired_gpus.append(gpu)
                self.gpu_status[gpu] = f"BUSY ({job_name})"

            if sorted_gpus:
                print(
                    f"[{job_name}] Acquired GPUs {sorted_gpus}. "
                    f"Running!"
                )
            else:
                print(f"[{job_name}] Running on CPU only!")

            # CPU scheduling / job execution simulation
            time.sleep(duration)
            print(f"[{job_name}] Finished successfully.")

        finally:
            # Release all resources even if a job fails
            for gpu in reversed(acquired_gpus):
                self.gpu_status[gpu] = "IDLE"
                self.gpu_locks[gpu].release()

            if allocated_ram:
                with self.ram_lock:
                    self.available_ram_gb += req_ram

            with self.active_jobs_lock:
                if job_name in self.active_jobs:
                    self.active_jobs.remove(job_name)

            self.job_queue.task_done()

    def shutdown(self):
        """Wait for jobs to finish before shutting down."""
        self.job_queue.join()
        self.is_running = False
        self.scheduler_thread.join()
        time.sleep(2)
        print("\n=== Cluster OS Shutdown Gracefully ===")


def main():
    # Create a sample dataset for the simulation
    with open("secure_dataset.csv", "w") as f:
        f.write("dummy data")

    print("=== Booting AI Cluster OS (64GB RAM, 4 GPUs) ===")

    os_system = AIClusterOS(total_ram_gb=64, num_gpus=4)

    # Workload A: Distributed training
    os_system.submit_job(
        "Workload_A_LLaMA",
        "secure_dataset.csv",
        req_ram=40,
        req_gpus=[2, 1, 0],
        duration=8
    )

    time.sleep(1)

    # Workload B: Data preprocessing, CPU only
    os_system.submit_job(
        "Workload_B_Preproc",
        "secure_dataset.csv",
        req_ram=16,
        req_gpus=[],
        duration=6
    )

    time.sleep(1)

    # Workload C: Inference API on GPU 3
    os_system.submit_job(
        "Workload_C_Infer",
        "secure_dataset.csv",
        req_ram=2,
        req_gpus=[3],
        duration=3
    )

    time.sleep(1)

    # Workload D: Missing file test
    os_system.submit_job(
        "Workload_D_Hacker",
        "secret_keys.txt",
        req_ram=1,
        req_gpus=[],
        duration=1
    )

    # Wait for all jobs to finish
    os_system.shutdown()

    # Clean up the sample dataset
    if os.path.exists("secure_dataset.csv"):
        os.remove("secure_dataset.csv")


if __name__ == "__main__":
    main()