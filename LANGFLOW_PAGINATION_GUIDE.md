# LangFlow Pagination Guide

## Issues Fixed

✅ **Pagination Logic**: Backend pagination is working correctly - tested with offsets 0, 10, 20, 30  
✅ **Output Format**: Removed emojis to fix encoding issues, cleaned up table structure  
✅ **next_offset Extraction**: Made next_offset more prominent in output for easier extraction  
✅ **Directory Validation**: Added proper directory existence checks  

## How to Use Pagination in LangFlow

### Step 1: Get Pagination Information
Use the `get_pagination_info` tool to see the complete pagination plan:
- **Input**: Directory path, batch size
- **Output**: Total files, total batches, all offset values

### Step 2: Start with First Batch
Use `list_files_table` with offset=0:
- **Input**: Directory path, offset="0", batch_size=10
- **Output**: First batch of files + next_offset value

### Step 3: Extract next_offset
From the output, look for the line:
```
| next_offset | 10 | Use this value for next batch | Batch size: 10 |
```
The value "10" is your next offset.

### Step 4: Continue Iteration
Use `list_files_table` with the extracted offset:
- **Input**: Directory path, offset="10", batch_size=10
- **Output**: Second batch of files + next_offset value

### Step 5: Repeat Until Complete
Continue extracting next_offset and using it for the next batch until no more files.

## LangFlow Flow Setup

1. **Chat Node**: Ask user for directory path
2. **get_pagination_info Node**: Get pagination plan
3. **list_files_table Node**: Get first batch (offset="0")
4. **Write File Node**: Save output to file
5. **Chat Node**: Extract next_offset from file content
6. **list_files_table Node**: Get next batch (offset=extracted_value)
7. **Append File Node**: Add to existing file
8. **Loop**: Repeat steps 5-7 until complete

## Next_Offset Extraction Logic

### Method 1: Using Chat Node with Prompt Engineering

**Chat Node Configuration:**
```
System Message: You are a data extraction assistant. Extract the next_offset value from the provided table output.

User Message: Extract the next_offset value from this output. Look for a line that starts with "| next_offset |" and return only the number after the pipe symbol. If no next_offset is found, return "DONE".

Output: {output_from_list_files_table}
```

**Expected Response:** The Chat node will return either a number (like "10") or "DONE" if no more files.

### Method 2: Using Python Function Node

**Python Function Node Code:**
```python
def extract_next_offset(output_text):
    """Extract next_offset from list_files_table output"""
    lines = output_text.split('\n')
    for line in lines:
        if '| next_offset |' in line:
            # Extract the number after the pipe
            parts = line.split('|')
            if len(parts) >= 3:
                offset_value = parts[2].strip()
                return offset_value
    return "DONE"  # No more files

# Usage
next_offset = extract_next_offset(input_text)
return {"next_offset": next_offset}
```

### Method 3: Using Regex in Chat Node

**Chat Node with Regex Prompt:**
```
Extract the next_offset value using this pattern:
- Look for: \| next_offset \| (\d+) \|
- Return only the number
- If pattern not found, return "DONE"

Output to analyze: {output_from_list_files_table}
```

## Loop Implementation Strategies

### Strategy 1: Manual Loop with Chat Control

**Flow Structure:**
1. **Chat Node**: "Enter directory path and batch size"
2. **get_pagination_info**: Get pagination plan
3. **list_files_table**: Get first batch (offset="0")
4. **Write File**: Save to `directory_list.txt`
5. **Chat Node**: Extract next_offset
6. **Conditional Chat**: "Continue with next batch? (yes/no)"
7. **If yes**: 
   - **list_files_table**: Use extracted offset
   - **Append File**: Add to `directory_list.txt`
   - **Chat Node**: Extract next_offset
   - **Loop back to step 6**
8. **If no**: End

### Strategy 2: Automated Loop with Counter

**Flow Structure:**
1. **Chat Node**: "Enter directory path"
2. **get_pagination_info**: Get total batches
3. **Initialize Counter**: Set counter = 0
4. **list_files_table**: Use offset = counter * batch_size
5. **Write/Append File**: Save output
6. **Chat Node**: Extract next_offset
7. **Conditional Logic**: 
   - If next_offset != "DONE": counter += 1, loop to step 4
   - If next_offset == "DONE": End

### Strategy 3: Smart Loop with Progress Tracking

**Flow Structure:**
1. **Chat Node**: "Enter directory path"
2. **get_pagination_info**: Get total files and batches
3. **Initialize Variables**: 
   - current_offset = "0"
   - total_files = from pagination info
   - processed_files = 0
4. **list_files_table**: Use current_offset
5. **Append File**: Add to output
6. **Chat Node**: Extract next_offset and count files in batch
7. **Update Progress**: 
   - processed_files += files_in_batch
   - current_offset = next_offset
8. **Conditional Logic**:
   - If processed_files < total_files: Loop to step 4
   - If processed_files >= total_files: End

## Smart Loop with Progress Tracking - Detailed Implementation

### Overview
The Smart Loop with Progress Tracking is the most robust approach for handling large directories. It tracks progress, handles edge cases, and provides safety mechanisms to prevent infinite loops.

### Step-by-Step Implementation

#### **Node 1: User Input (Chat)**
```
System Message: You are a directory listing assistant. Ask the user for the directory path they want to list.

User Message: Please provide the directory path you want to list all files from. I'll create a complete directory listing with pagination.
```

#### **Node 2: Get Pagination Information (Tool)**
```
Tool: get_pagination_info
Input:
- directory: {user_directory}
- batch_size: 10
- max_depth: 1
- include_hidden: false
```

#### **Node 3: Initialize Progress Variables (Chat)**
```
System Message: You are a progress tracking assistant. Extract total files from pagination info and initialize progress variables.

User Message: Extract the total number of files from this pagination information and initialize progress tracking variables. Return a JSON object with: {"total_files": number, "current_offset": "0", "processed_files": 0, "batch_size": 10, "status": "STARTING"}

Pagination Info: {output_from_node_2}
```

#### **Node 4: First Batch (Tool)**
```
Tool: list_files_table
Input:
- directory: {user_directory}
- offset: "0"
- batch_size: 10
- max_depth: 1
- include_hidden: false
- file_types: []
- sort_by: "name"
- sort_order: "asc"
```

#### **Node 5: Write Initial File (Tool)**
```
Tool: write_file
Input:
- file_path: "complete_directory_list.txt"
- content: {output_from_node_4}
```

#### **Node 6: Extract Progress Information (Chat)**
```
System Message: You are a data extraction assistant. Extract next_offset and count files in the current batch from the table output.

User Message: From this table output, extract:
1. The next_offset value (look for "| next_offset |" line)
2. Count the number of file/directory rows (exclude summary, pagination, and next_offset rows)

Return a JSON object: {"next_offset": "number_or_DONE", "files_in_batch": number, "current_output": "full_output"}

Table Output: {output_from_node_4}
```

#### **Node 7: Update Progress (Chat)**
```
System Message: You are a progress tracking assistant. Update progress variables and determine if we should continue.

User Message: Update the progress tracking and determine if we should continue pagination.

Current Progress: {progress_from_node_3}
Extracted Info: {extracted_info_from_node_6}

Update the progress and return:
{"total_files": number, "current_offset": "new_offset", "processed_files": updated_count, "batch_size": 10, "status": "CONTINUE_or_COMPLETE"}

Rules:
- If next_offset is "DONE", set status to "COMPLETE"
- If processed_files >= total_files, set status to "COMPLETE"
- Otherwise, set status to "CONTINUE"
- Add files_in_batch to processed_files
- Set current_offset to next_offset
```

#### **Node 8: Conditional Logic (Chat)**
```
System Message: You are a flow control assistant. Determine the next action based on progress status.

User Message: Based on the progress status, determine what to do next:
- If status is "CONTINUE": respond with "CONTINUE_PAGINATION"
- If status is "COMPLETE": respond with "PAGINATION_COMPLETE"
- If status is "ERROR": respond with "ERROR_OCCURRED"

Progress: {updated_progress_from_node_7}
```

#### **Node 9: Next Batch (Tool) - Conditional**
```
Tool: list_files_table
Input:
- directory: {user_directory}
- offset: {current_offset_from_node_7}
- batch_size: 10
- max_depth: 1
- include_hidden: false
- file_types: []
- sort_by: "name"
- sort_order: "asc"
```

#### **Node 10: Append to File (Tool) - Conditional**
```
Tool: append_file
Input:
- file_path: "complete_directory_list.txt"
- content: {output_from_node_9}
```

#### **Node 11: Loop Back to Progress Extraction (Chat)**
```
System Message: You are a loop control assistant. Continue the pagination loop.

User Message: Continue with the next iteration. Extract progress information from the new batch output.

Current Progress: {progress_from_node_7}
New Batch Output: {output_from_node_9}
```

### Flow Connections

**Main Flow:**
1. Node 1 → Node 2 → Node 3 → Node 4 → Node 5 → Node 6 → Node 7 → Node 8

**Conditional Branch 1 (Continue):**
- Node 8 (CONTINUE_PAGINATION) → Node 9 → Node 10 → Node 11 → Node 6

**Conditional Branch 2 (Complete):**
- Node 8 (PAGINATION_COMPLETE) → Final Summary Node

### Safety Mechanisms

#### **1. Maximum Iteration Counter**
Add a safety counter to prevent infinite loops:
```python
# In Node 7 (Update Progress)
max_iterations = 1000  # Adjust based on expected directory size
if iteration_count > max_iterations:
    status = "ERROR_MAX_ITERATIONS"
```

#### **2. Progress Validation**
Validate that progress is moving forward:
```python
# In Node 7 (Update Progress)
if processed_files > total_files:
    status = "ERROR_OVERFLOW"
```

#### **3. Timeout Protection**
Add timestamp tracking to prevent hanging:
```python
# In Node 7 (Update Progress)
import time
if time.time() - start_time > 300:  # 5 minutes timeout
    status = "ERROR_TIMEOUT"
```

### Error Handling

#### **Common Error Scenarios:**
1. **Directory not found**: Handle in Node 2
2. **Permission denied**: Handle in Node 2
3. **Invalid offset**: Handle in Node 6
4. **File write errors**: Handle in Node 5 and Node 10
5. **Network timeouts**: Handle with retry logic

#### **Error Recovery:**
```python
# In Node 8 (Conditional Logic)
if status.startswith("ERROR"):
    # Log error and attempt recovery
    if "TIMEOUT" in status:
        return "RETRY_WITH_SMALLER_BATCH"
    elif "MAX_ITERATIONS" in status:
        return "PAGINATION_COMPLETE_WITH_WARNING"
    else:
        return "ERROR_OCCURRED"
```

### Progress Reporting

#### **Real-time Progress Updates:**
```python
# In Node 7 (Update Progress)
progress_percentage = (processed_files / total_files) * 100
progress_message = f"Processed {processed_files}/{total_files} files ({progress_percentage:.1f}%)"
```

#### **Final Summary:**
```python
# Final Summary Node
summary = f"""
Directory listing complete!
- Total files processed: {processed_files}
- Total batches: {batch_count}
- Output file: complete_directory_list.txt
- Processing time: {total_time} seconds
"""
```

### Advantages of Smart Loop with Progress Tracking

1. **Robust Error Handling**: Catches and handles various error conditions
2. **Progress Monitoring**: Real-time tracking of completion status
3. **Safety Mechanisms**: Prevents infinite loops and timeouts
4. **Flexible Termination**: Multiple ways to detect completion
5. **Debugging Support**: Clear progress indicators for troubleshooting
6. **Scalable**: Works with directories of any size
7. **Resumable**: Can be modified to resume from a specific offset

### Testing the Implementation

#### **Test with Small Directory:**
1. Use a directory with 5-10 files
2. Set batch_size to 3
3. Verify 2-3 iterations complete correctly

#### **Test with Large Directory:**
1. Use a directory with 100+ files
2. Set batch_size to 10
3. Verify all files are processed

#### **Test Error Conditions:**
1. Use non-existent directory
2. Use directory with permission issues
3. Test with very large batch sizes

This Smart Loop implementation provides the most reliable and maintainable approach for handling directory pagination in LangFlow.

## Example LangFlow Flow Configuration

### Node 1: User Input (Chat)
```
System: You are a directory listing assistant.
User: Please list all files in directory: {user_directory}
```

### Node 2: Pagination Info (Tool)
```
Tool: get_pagination_info
Input: 
- directory: {user_directory}
- batch_size: 10
```

### Node 3: First Batch (Tool)
```
Tool: list_files_table
Input:
- directory: {user_directory}
- offset: "0"
- batch_size: 10
```

### Node 4: Write Initial File (Tool)
```
Tool: write_file
Input:
- file_path: "directory_list.txt"
- content: {output_from_node_3}
```

### Node 5: Extract Next Offset (Chat)
```
System: Extract the next_offset value from the table output.
User: Extract next_offset from: {output_from_node_3}
```

### Node 6: Check Continue (Chat)
```
System: Determine if we should continue pagination.
User: If the extracted value is "DONE", respond with "STOP". Otherwise, respond with "CONTINUE: {extracted_offset}"
```

### Node 7: Next Batch (Tool) - Conditional
```
Tool: list_files_table
Input:
- directory: {user_directory}
- offset: {extracted_offset}
- batch_size: 10
```

### Node 8: Append to File (Tool) - Conditional
```
Tool: append_file
Input:
- file_path: "directory_list.txt"
- content: {output_from_node_7}
```

## Troubleshooting

### If pagination seems stuck:
1. Check that you're extracting the correct next_offset value
2. Verify the offset is being passed as a string to the tool
3. Ensure the directory path is correct and accessible

### If get_pagination_info shows "0 files":
1. Check the directory path - it might be incorrect
2. Verify the directory exists and is accessible
3. Try with a different directory path

### If output format looks wrong:
1. Restart the MCP server to get the latest changes
2. Clear any cached data in LangFlow
3. Check that you're using the `list_files_table` tool (not `list_files`)

### If loop doesn't terminate:
1. Check your conditional logic in Chat nodes
2. Verify that "DONE" is being returned when no more files
3. Add a maximum iteration counter as safety

## Example Output Format

```
| summary | Directory: D:\path\to\directory | Directory listing | Total: 116 files, 16 directories | Size: 0.81 MB | Processed: 2025-08-02T14:43:34.969614 |
| directory | __pycache__ | Directory | Modified: 2025-08-02 14:43:34 | Type: Directory |
| .md | ACTUAL_STATUS.md | Documentation | Size: 0.01 MB | Modified: 2025-07-29 22:30:59 | Extension: .md |
| pagination | Showing batch 1-5 of 116 | More files available | Next offset: 5 | Processing time: 0.01s |
| next_offset | 5 | Use this value for next batch | Batch size: 5 |
```

## Key Points

- **Offset is always a string** in LangFlow (e.g., "0", "10", "20")
- **next_offset is clearly marked** in the output for easy extraction
- **No more encoding issues** - emojis removed
- **Clean table format** - no nested structures
- **Proper validation** - directory existence checked
- **Loop termination** - Look for "DONE" or check if next_offset exists
- **Error handling** - Always validate extracted values before using them 