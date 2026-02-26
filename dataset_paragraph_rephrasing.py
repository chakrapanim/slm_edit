"""
Generate a dataset of 50 paragraph rephrasing examples for evaluation.
Each example: input paragraph (up to 512 tokens), 4 reference rephrasings.
Output: paragraph_rephrasing_dataset.csv
"""

import pandas as pd
from transformers import T5Tokenizer

MAX_INPUT_TOKENS = 512
NUM_EXAMPLES = 50
OUTPUT_CSV = "paragraph_rephrasing_dataset.csv"


def _token_count(tokenizer, text):
    return len(tokenizer.encode(text, max_length=2048, truncation=True))


def generate_paragraph_examples():
    """
    Returns list of (input_paragraph, [ref1, ref2, ref3, ref4]).
    Input paragraphs are wordy/formal; refs are clearer rephrasings.
    """
    # Building blocks: wordy sentences and their concise variants (4 each)
    # Each item: (wordy_paragraph, [ref1, ref2, ref3, ref4])
    # We combine 2-4 wordy sentences into a paragraph to reach paragraph length.
    blocks = [
        # 1
        (
            "It is important to note that the project timeline has been subject to significant delays. "
            "Due to the fact that we have been experiencing a variety of unforeseen circumstances, "
            "we are currently in the process of reassessing our approach. In order to complete the deliverables on schedule, "
            "it will be necessary for us to allocate additional resources to the task at hand.",
            [
                "The project timeline has been delayed. Unforeseen circumstances have forced us to reassess our approach. We need to allocate more resources to meet the schedule.",
                "Significant delays have affected the project. We're reassessing our approach due to unforeseen circumstances and will need more resources to complete deliverables on time.",
                "The project is behind schedule. We're reassessing and will need additional resources to complete deliverables on time.",
                "Delays have impacted the timeline. We're reassessing and must add resources to stay on schedule.",
            ],
        ),
        # 2
        (
            "In the event that you have any questions or concerns with regard to the proposal that has been put forward, "
            "please do not hesitate to get in touch with us at your earliest convenience. "
            "We are more than happy to provide you with any additional information that you may require "
            "in order to facilitate the decision-making process.",
            [
                "If you have questions about the proposal, contact us. We're happy to provide any information you need to decide.",
                "Contact us if you have questions or concerns about the proposal. We'll provide any information you need.",
                "Questions about the proposal? Contact us anytime. We can provide whatever information you need to decide.",
                "Reach out if you need more information or have concerns about the proposal.",
            ],
        ),
        # 3
        (
            "The committee has reached the conclusion that it would be in the best interests of all parties involved "
            "to postpone the meeting until such time as all of the relevant data has been compiled and reviewed. "
            "It is our expectation that this will allow for a more productive discussion and a better outcome for everyone.",
            [
                "The committee decided to postpone the meeting until all relevant data is compiled and reviewed. We expect a more productive discussion and better outcome.",
                "The committee concluded that postponing the meeting until data is compiled and reviewed is best. This should lead to a more productive discussion.",
                "We're postponing the meeting until we have and review all relevant data. We expect a better discussion and outcome.",
                "The meeting will be postponed until data is compiled and reviewed so we can have a more productive discussion.",
            ],
        ),
        # 4
        (
            "There are a number of different factors that need to be taken into consideration when we are in the process of "
            "making a decision with respect to the future direction of the company. The fact of the matter is that "
            "we need to ensure that we have a comprehensive understanding of the market conditions before we proceed.",
            [
                "Several factors must be considered when deciding the company's future direction. We need a comprehensive understanding of market conditions before proceeding.",
                "Many factors matter when deciding the company's direction. We must understand market conditions before we proceed.",
                "We must consider several factors before deciding the company's future direction and need a clear picture of market conditions.",
                "Before deciding the company's direction, we need to consider several factors and understand market conditions.",
            ],
        ),
        # 5
        (
            "It has come to our attention that there have been a series of complaints that have been submitted by customers "
            "in relation to the quality of the product that was delivered. We are currently in the process of "
            "conducting a thorough investigation into the matter in order to identify the root cause of the problem.",
            [
                "We've learned that customers have complained about the quality of the delivered product. We're investigating to find the root cause.",
                "Customers have submitted complaints about product quality. We're conducting a thorough investigation to identify the root cause.",
                "We're aware of customer complaints about delivered product quality and are investigating the root cause.",
                "Following customer complaints about product quality, we're investigating to identify the root cause.",
            ],
        ),
        # 6
        (
            "The implementation of the new policy is scheduled to take effect at the beginning of the next quarter. "
            "It is anticipated that this will result in a number of positive outcomes for the organization as a whole, "
            "including but not limited to improved efficiency and a reduction in operational costs. All employees are required to comply.",
            [
                "The new policy takes effect at the start of next quarter. We expect improved efficiency and lower operational costs. All employees must comply.",
                "The new policy goes into effect next quarter. We anticipate improved efficiency and reduced costs. Compliance is required for all employees.",
                "Starting next quarter, the new policy will bring improved efficiency and lower costs. All employees must comply.",
                "The new policy begins next quarter and should improve efficiency and reduce costs. All employees must comply.",
            ],
        ),
        # 7
        (
            "In spite of the fact that we have made every effort to complete the task within the specified timeframe, "
            "we have encountered a number of obstacles that have prevented us from doing so. We would like to request "
            "an extension of the deadline in order to ensure that we are able to deliver work of the highest quality.",
            [
                "Despite our efforts to meet the deadline, we've encountered obstacles. We request an extension to deliver high-quality work.",
                "We've tried to finish on time but faced obstacles. We're requesting a deadline extension so we can deliver quality work.",
                "Obstacles have prevented us from meeting the deadline despite our efforts. We request an extension to ensure quality.",
                "We request a deadline extension; we've encountered obstacles and want to deliver the highest quality work.",
            ],
        ),
        # 8
        (
            "The report that was prepared by the research team contains a great deal of valuable information that could be "
            "of use to us in the context of our strategic planning efforts. It is recommended that we take the time to "
            "review the document in detail prior to the upcoming planning session.",
            [
                "The research team's report contains valuable information for our strategic planning. We should review it in detail before the planning session.",
                "The report has valuable information for strategic planning. We recommend reviewing it in detail before the planning session.",
                "We should review the research team's report in detail before the planning session; it has valuable strategic planning information.",
                "The report holds valuable strategic planning information. Review it in detail before the upcoming planning session.",
            ],
        ),
        # 9
        (
            "As a result of the feedback that we have received from a variety of different sources, we have come to the "
            "conclusion that it would be beneficial for us to make a number of changes to the way in which we operate. "
            "We are in the process of developing a detailed plan that will outline the steps that need to be taken.",
            [
                "Feedback from various sources has led us to conclude that we should change how we operate. We're developing a detailed plan.",
                "Based on feedback from many sources, we've decided to make operational changes. We're developing a detailed plan for next steps.",
                "We've decided to change our operations based on feedback. We're developing a detailed plan with the steps to take.",
                "Feedback led us to plan operational changes. We're developing a detailed plan outlining the necessary steps.",
            ],
        ),
        # 10
        (
            "The meeting that was held on Monday was attended by representatives from each of the departments that are "
            "involved in the project. A great deal of progress was made with regard to the identification of the key "
            "milestones that will need to be achieved over the course of the next six months.",
            [
                "Monday's meeting included representatives from each project department. We made progress identifying key milestones for the next six months.",
                "Representatives from every project department attended Monday's meeting. We identified key milestones for the next six months.",
                "At Monday's meeting, department representatives made progress identifying key milestones for the next six months.",
                "The Monday meeting had all project departments represented. Key milestones for the next six months were identified.",
            ],
        ),
    ]

    # Add more paragraph blocks to reach 50 (reuse and vary)
    extra_blocks = [
        (
            "In view of the fact that the budget has been approved by the board of directors, we are now in a position to "
            "move forward with the implementation of the first phase of the project. It is our intention to begin the work "
            "as soon as possible and to keep all stakeholders informed of our progress on a regular basis.",
            [
                "The board has approved the budget, so we can move forward with the first phase. We'll start as soon as possible and keep stakeholders informed.",
                "With budget approval from the board, we're moving forward with phase one. We intend to start soon and update stakeholders regularly.",
                "Budget approved; we're starting phase one implementation and will keep stakeholders informed.",
                "We can now implement phase one and will start soon, keeping stakeholders updated.",
            ],
        ),
        (
            "The purpose of this document is to provide you with a summary of the findings that were uncovered during the "
            "course of our investigation. We have attempted to present the information in a clear and concise manner so that "
            "it can be easily understood by all parties who have an interest in the outcome.",
            [
                "This document summarizes our investigation findings. We've presented the information clearly for all interested parties.",
                "Here we summarize the investigation findings in a clear, concise way for all interested parties.",
                "We present our investigation findings in this document in a clear and concise manner.",
                "This document clearly summarizes our investigation findings for all interested parties.",
            ],
        ),
        (
            "At the present time, we are experiencing a situation where the demand for our products has exceeded our initial "
            "expectations. As a consequence of this, we are currently in the process of exploring a number of different "
            "options that would allow us to increase our production capacity in order to meet the needs of our customers.",
            [
                "Demand for our products has exceeded expectations. We're exploring options to increase production capacity to meet customer needs.",
                "We're seeing higher demand than expected and are exploring ways to increase production to meet customer needs.",
                "Demand exceeds expectations; we're exploring options to increase production capacity.",
                "We're exploring ways to increase production to meet the higher-than-expected demand.",
            ],
        ),
    ]
    blocks.extend(extra_blocks)

    # Build 50 examples with varied length: single block (~60-80 tokens), double (120-160), triple (180-240), longer (300-400+)
    def combine(block_list):
        """Combine multiple (input, refs) into one (long_input, long_refs)."""
        inputs = [b[0] for b in block_list]
        refs_list = [b[1] for b in block_list]
        long_input = " ".join(inputs)
        long_refs = [" ".join(refs_list[k][j] for k in range(len(block_list))) for j in range(4)]
        return long_input, long_refs

    expanded = []
    for i in range(NUM_EXAMPLES):
        if i < 15:
            b = blocks[i % len(blocks)]
            input_p, refs = b[0], list(b[1])
        elif i < 30:
            b1, b2 = blocks[i % len(blocks)], blocks[(i + 1) % len(blocks)]
            input_p, refs = combine([b1, b2])
        elif i < 40:
            b1, b2, b3 = blocks[i % len(blocks)], blocks[(i + 1) % len(blocks)], blocks[(i + 2) % len(blocks)]
            input_p, refs = combine([b1, b2, b3])
        elif i < 48:
            b1, b2, b3, b4 = blocks[i % len(blocks)], blocks[(i + 1) % len(blocks)], blocks[(i + 2) % len(blocks)], blocks[(i + 3) % len(blocks)]
            input_p, refs = combine([b1, b2, b3, b4])
        else:
            b1, b2, b3, b4, b5 = [blocks[(i + k) % len(blocks)] for k in range(5)]
            input_p, refs = combine([b1, b2, b3, b4, b5])
        if i >= len(blocks):
            refs = refs[i % 4:] + refs[:i % 4]
        expanded.append((input_p, refs))
    return expanded


def main():
    print("Generating paragraph rephrasing dataset (50 examples, max 512 tokens per input)...")
    tokenizer = T5Tokenizer.from_pretrained("Vennify/t5-base-grammar-correction")
    examples = generate_paragraph_examples()
    rows = []
    for idx, (input_para, refs) in enumerate(examples):
        tc = _token_count(tokenizer, input_para)
        if tc > MAX_INPUT_TOKENS:
            # Truncate by words to stay under (rough)
            words = input_para.split()
            approx_tokens = 0
            trunc = []
            for w in words:
                trunc.append(w)
                approx_tokens += 1 + len(w) // 4
                if approx_tokens >= MAX_INPUT_TOKENS:
                    break
            input_para = " ".join(trunc)
        rows.append({
            "Index": idx,
            "Category": "Rephrasing",
            "Input_Text": input_para,
            "Ground_Truth": refs[0],
            "All_References": "|".join(refs),
        })
    df = pd.DataFrame(rows)
    # Verify token counts
    df["Input_Tokens"] = df["Input_Text"].apply(lambda t: _token_count(tokenizer, t))
    assert (df["Input_Tokens"] <= MAX_INPUT_TOKENS).all(), "Some inputs exceed 512 tokens"
    df.drop(columns=["Input_Tokens"], inplace=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} examples to {OUTPUT_CSV}")
    print(f"Input token range: {df['Input_Text'].apply(lambda t: _token_count(tokenizer, t)).min()} - {df['Input_Text'].apply(lambda t: _token_count(tokenizer, t)).max()}")
    return df


if __name__ == "__main__":
    main()
