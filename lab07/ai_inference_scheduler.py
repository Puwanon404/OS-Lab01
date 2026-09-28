
# ai_inference_scheduler.py

import time


class AIRequest:
    def __init__(self, user_id, tokens_required):
        self.user_id = user_id
        self.tokens_required = tokens_required
        self.tokens_generated = 0


def simulate_ai_fcfs(requests):
    print("\n[AI Server] Strategy: First-Come, First-Served")

    for req in requests:
        print(
            f"-> Starting {req.user_id} "
            f"(Needs {req.tokens_required} tokens)..."
        )

        time.sleep(0.5)  # Simulate GPU computation

        print(f" [DONE] {req.user_id} finished. Responded perfectly.")


def simulate_ai_round_robin(requests):
    print("\n[AI Server] Strategy: Round Robin (Token-by-Token Continuous Batching)")

    queue = list(requests)

    while queue:
        req = queue.pop(0)

        # Generate one token at a time
        req.tokens_generated += 1

        if req.tokens_generated == req.tokens_required:
            print(
                f" [DONE] {req.user_id} finished early! "
                f"(Total: {req.tokens_required} tokens)"
            )
        else:
            # Put unfinished request at the back of the queue
            queue.append(req)

        time.sleep(0.05)  # Simulate fast token generation


def main():
    print("--- Incoming API Requests ---")

    # Requests for FCFS
    reqs_fcfs = [
        AIRequest("User_A_Essay", 10),
        AIRequest("User_B_Math", 2)
    ]
    simulate_ai_fcfs(reqs_fcfs)

    # New requests for Round Robin
    reqs_rr = [
        AIRequest("User_A_Essay", 10),
        AIRequest("User_B_Math", 2)
    ]
    simulate_ai_round_robin(reqs_rr)


if __name__ == "__main__":
    main()