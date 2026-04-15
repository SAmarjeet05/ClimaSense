"""
MAP ACTION INTEGRATION GUIDE
Frontend implementation for AI Assistant navigation

WHAT THIS DOES:
When a user asks "Show rainfall map" or "Display temperature on map":
1. Backend detects this as "map_action" intent
2. Returns navigation instructions with map_mode (risk/temperature/rainfall)
3. Frontend automatically navigates to the map with the specified visualization layer

IMPLEMENTATION STEPS:
"""

# ===========================================================================
# STEP 1: Update your Chat/Assistant Response Handler in React
# ===========================================================================

example_response_handler = """
// In your Chat component or wherever you handle assistant responses

const handleAssistantResponse = (response) => {
  // Check if this is a map action response
  if (response.intent === 'map_action' || response.action === 'navigate_map') {
    // Extract the map mode (risk, temperature, rainfall)
    const mapMode = response.map_mode;
    
    // Navigate to map with the mode parameter
    navigate('/map', { 
      state: { 
        mode: mapMode,
        message: response.message 
      } 
    });
    
    // Show confirmation message (optional)
    showNotification(`Opening ${mapMode} map...`);
    return;
  }
  
  // Handle other response types normally
  if (response.intent === 'compare') {
    // ... existing comparison handling
  }
  // ... etc
};
"""

# ===========================================================================
# STEP 2: Update your Map Component to Accept Mode Parameter
# ===========================================================================

example_map_component = """
// In your Map.tsx or Map component

import { useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';

export function ClimateMap() {
  const [mode, setMode] = useState('temperature'); // Default mode
  const location = useLocation();
  
  useEffect(() => {
    // Check if we came from assistant with a specific mode
    if (location.state?.mode) {
      const requestedMode = location.state.mode;
      
      // Validate mode
      if (['risk', 'temperature', 'rainfall'].includes(requestedMode)) {
        setMode(requestedMode);
        console.log(`Map opened with ${requestedMode} visualization`);
        
        // Optional: Show toast showing what layer is active
        if (location.state?.message) {
          showToast(location.state.message);
        }
      }
    }
  }, [location.state]);
  
  return (
    <div className="map-container">
      {/* Map mode switcher */}
      <div className="map-controls">
        <button 
          onClick={() => setMode('temperature')}
          className={mode === 'temperature' ? 'active' : ''}
        >
          Temperature
        </button>
        <button 
          onClick={() => setMode('rainfall')}
          className={mode === 'rainfall' ? 'active' : ''}
        >
          Rainfall
        </button>
        <button 
          onClick={() => setMode('risk')}
          className={mode === 'risk' ? 'active' : ''}
        >
          Risk
        </button>
      </div>
      
      {/* Render appropriate map layer based on mode */}
      <MapLayer mode={mode} />
    </div>
  );
}
"""

# ===========================================================================
# STEP 3: Backend Response Format
# ===========================================================================

example_backend_response = {
    "status": "success",
    "intent": "map_action",
    "query": "Show rainfall map",
    "action": "navigate_map",
    "map_mode": "rainfall",
    "message": "Showing rainfall distribution on map",
    "suggested_action": "View rainfall map",
    "action_url": "/map?mode=rainfall",
    "timestamp": "2026-04-15T10:30:00"
}

# ===========================================================================
# STEP 4: Complete Integration Example for React
# ===========================================================================

complete_example = """
// In your ChatInterface.tsx

interface AssistantResponse {
  intent: string;
  action?: string;
  map_mode?: string;
  message?: string;
  answer?: string;
  // ... other fields
}

export function ChatInterface() {
  const navigate = useNavigate();
  
  const processAssistantResponse = (response: AssistantResponse) => {
    // Priority 1: Check for map_action
    if (response.intent === 'map_action') {
      const mode = response.map_mode || 'temperature';
      
      // Navigate to map with auto-switching
      navigate('/map', { 
        replace: true,
        state: { 
          visualizationMode: mode,
          fromAssistant: true,
          message: response.message
        } 
      });
      return;
    }
    
    // Priority 2: Regular data responses
    setConversation([
      ...conversation,
      {
        type: 'assistant',
        content: response.answer,
        intent: response.intent,
        data: response.data
      }
    ]);
  };
  
  return (
    <div className="chat-interface">
      <ChatMessages 
        messages={conversation}
        onResponseClick={processAssistantResponse}
      />
      {/* ... rest of chat UI */}
    </div>
  );
}
"""

# ===========================================================================
# SUPPORTED QUERIES
# ===========================================================================

supported_queries = [
    "Show high risk cities on map",          # → map_mode: 'risk'
    "Display temperature distribution",       # → map_mode: 'temperature' 
    "Show rainfall map",                      # → map_mode: 'rainfall'
    "Display temperature on map",             # → map_mode: 'temperature'
    "Can you show me the temperature map?",  # → map_mode: 'temperature'
    "Show me the risk map",                  # → map_mode: 'risk'
    "Display rainfall visualization",         # → map_mode: 'rainfall'
]

# ===========================================================================
# EDGE CASES TO HANDLE
# ===========================================================================

edge_cases = """
1. User asks "Show map" without specifying mode
   → Defaults to 'temperature' mode
   → Backend returns: map_mode: 'temperature'

2. User asks "Compare Delhi and Mumbai on map"
   → Does NOT trigger map_action
   → Triggers "compare" intent instead
   → Shows comparison data normally

3. User asks "Show me the risk analysis" 
   → Does NOT trigger map_action
   → Triggers "risk" intent
   → Returns risk analysis text

4. User navigates away from map and comes back
   → location.state?.mode will be undefined
   → Uses default 'temperature' mode
   → This is correct behavior
"""

# ===========================================================================
# TESTING IN YOUR FRONTEND
# ===========================================================================

testing_code = """
// Test your frontend integration

describe('Map Action Integration', () => {
  test('navigates to map with risk mode', () => {
    const response = {
      intent: 'map_action',
      map_mode: 'risk',
      message: 'Showing risk distribution on map'
    };
    
    const { navigate } = useNavigate();
    processAssistantResponse(response);
    
    expect(navigate).toHaveBeenCalledWith('/map', expect.objectContaining({
      state: { mode: 'risk' }
    }));
  });
  
  test('uses temperature as default mode', () => {
    const response = {
      intent: 'map_action',
      map_mode: undefined
    };
    
    const { navigate } = useNavigate();
    processAssistantResponse(response);
    
    expect(navigate).toHaveBeenCalledWith('/map', expect.objectContaining({
      state: { mode: 'temperature' }
    }));
  });
});
"""

print(__doc__)
print("\nExample Response Handler:")
print(example_response_handler)
print("\nExample Map Component Update:")
print(example_map_component)
print("\nBackend Response Format:")
print(example_backend_response)
print("\nComplete Integration Example:")
print(complete_example)
print("\nSupported Queries:")
print(supported_queries)
print("\nEdge Cases:")
print(edge_cases)
print("\nTesting Code:")
print(testing_code)

print("\n" + "="*75)
print("✅ MAP ACTION FEATURE IS READY FOR FRONTEND INTEGRATION")
print("="*75)
print("\n🎯 Next Steps:")
print("  1. Update your Chat component to detect map_action responses")
print("  2. Implement navigation to /map with state.mode parameter")
print("  3. Update Map component to read location.state.mode")
print("  4. Switch visualization layers based on mode")
print("\n")
