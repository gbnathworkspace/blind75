from typing import List, Optional
import heapq


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        newLLlist = ListNode()

        h = []        
        
        for list in lists:
            curr = list
            while (curr is not None):
                print(curr.val)
                heapq.heappush(h, curr.val)
                curr = curr.next

        if(len(h)==0):
            return None

        # this was the hardest part
        x1 = heapq.heappop(h)
        newNode = ListNode(x1)
        traveringNode = newNode
        while len(h)>0:
            x = heapq.heappop(h)
            traveringNode.next = ListNode(x)
            traveringNode = traveringNode.next            
        
        return newNode
































# Helper: Convert Python list to Linked List
def create_linked_list(values):
    dummy = ListNode()
    current = dummy

    for value in values:
        current.next = ListNode(value)
        current = current.next

    return dummy.next


# Helper: Convert Linked List to Python list
def linked_list_to_list(head):
    result = []

    while head:
        result.append(head.val)
        head = head.next

    return result


# Test cases
def run_test(lists, expected):
    linked_lists = [create_linked_list(lst) for lst in lists]

    solution = Solution()
    result = solution.mergeKLists(linked_lists)

    actual = linked_list_to_list(result)

    print(f"Input:    {lists}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    print(f"Result:   {'PASS' if actual == expected else 'FAIL'}")
    print("-" * 50)


if __name__ == "__main__":

    # Test Case 1: Standard case
    run_test(
        [[1, 4, 5], [1, 3, 4], [2, 6]],
        [1, 1, 2, 3, 4, 4, 5, 6]
    )

    # Test Case 2: Empty input
    run_test(
        [],
        []
    )

    # Test Case 3: Empty linked list
    run_test(
        [[]],
        []
    )

    # Test Case 4: Single linked list
    run_test(
        [[1, 2, 3]],
        [1, 2, 3]
    )

    # Test Case 5: Multiple empty lists
    run_test(
        [[], [], []],
        []
    )

    # Test Case 6: Negative numbers
    run_test(
        [[-5, -1, 3], [-4, 0, 2]],
        [-5, -4, -1, 0, 2, 3]
    )

    # Test Case 7: Duplicate values
    run_test(
        [[1, 1, 1], [1, 1], [1]],
        [1, 1, 1, 1, 1, 1]
    )