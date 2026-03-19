---
name: excalidraw-diagram-generator
description: "Generates visual diagrams from natural language descriptions, outputting .excalidraw JSON files. Supports flowcharts, relationship diagrams, mind maps, architecture diagrams, data flow diagrams, business flows, class diagrams, sequence diagrams, and ER diagrams."
---

# Excalidraw Diagram Generator

Generates visual diagrams from natural language descriptions, outputting `.excalidraw` JSON files compatible with Excalidraw's platform.

## Supported Diagram Types

1. Flowcharts
2. Relationship diagrams
3. Mind maps
4. Architecture diagrams
5. Data flow diagrams
6. Business flows
7. Class diagrams
8. Sequence diagrams
9. Entity-relationship diagrams

## Workflow

1. **Analyze the request** to identify diagram type, key elements, and relationships
2. **Select the appropriate diagram format** based on user intent (e.g., "workflow" suggests flowcharts)
3. **Extract structured information** specific to that diagram type
4. **Generate Excalidraw JSON** with properly positioned elements
5. **Format the complete output** as valid JSON with metadata
6. **Deliver with instructions** for opening files in Excalidraw

## Technical Requirements

- All text elements must use fontFamily: 5 (Excalifont) for consistent visual appearance
- Maintain reasonable element counts (typically under 20)
- Recommended spacing: 200-300px horizontally, 100-150px vertically
- Validate before delivery: unique IDs, readable text, logical connections, consistent color schemes

## Icon Integration (Advanced)

For specialized diagrams, Python scripts can automatically integrate icons from downloaded `.excalidrawlib` libraries. Users can set up libraries from https://libraries.excalidraw.com/.

## Activation Triggers

"create a diagram", "make a flowchart", "visualize a process", "draw architecture", "ER diagram", "mind map"
