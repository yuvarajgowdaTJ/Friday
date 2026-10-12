import React, { useState } from 'react';
import { Search, Trash2, Plus, Brain, X } from 'lucide-react';

export interface MemoryItemData {
  id: number;
  key: string;
  value: string;
  category: string;
  created_at?: string;
}

interface MemoryExplorerProps {
  memories: MemoryItemData[];
  onAddMemory: (key: string, value: string) => void;
  onDeleteMemory: (id: number) => void;
  onSearch: (query: string) => void;
  onClose?: () => void;
}

export const MemoryExplorer: React.FC<MemoryExplorerProps> = ({
  memories,
  onAddMemory,
  onDeleteMemory,
  onSearch,
  onClose,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    onSearch(e.target.value);
  };

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;
    onAddMemory(newKey, newValue);
    setNewKey('');
    setNewValue('');
    setShowAddForm(false);
  };

  return (
    <div
      className="flex flex-col h-full select-none"
      style={{
        background: 'linear-gradient(135deg, #000000 0%, #020818 60%, #030d1f 100%)',
        border: '1px solid rgba(0, 255, 255, 0.18)',
        boxShadow: '0 0 24px rgba(0, 255, 255, 0.06), inset 0 1px 0 rgba(0, 255, 255, 0.08)',
        borderRadius: '6px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Corner accents */}
      <span style={{ position: 'absolute', top: 0, left: 0, width: 14, height: 14, borderTop: '1px solid rgba(0,255,255,0.5)', borderLeft: '1px solid rgba(0,255,255,0.5)', borderRadius: '2px 0 0 0', pointerEvents: 'none' }} />
      <span style={{ position: 'absolute', top: 0, right: 0, width: 14, height: 14, borderTop: '1px solid rgba(0,255,255,0.5)', borderRight: '1px solid rgba(0,255,255,0.5)', borderRadius: '0 2px 0 0', pointerEvents: 'none' }} />
      <span style={{ position: 'absolute', bottom: 0, left: 0, width: 14, height: 14, borderBottom: '1px solid rgba(0,255,255,0.5)', borderLeft: '1px solid rgba(0,255,255,0.5)', borderRadius: '0 0 0 2px', pointerEvents: 'none' }} />
      <span style={{ position: 'absolute', bottom: 0, right: 0, width: 14, height: 14, borderBottom: '1px solid rgba(0,255,255,0.5)', borderRight: '1px solid rgba(0,255,255,0.5)', borderRadius: '0 0 2px 0', pointerEvents: 'none' }} />

      {/* Header */}
      <div
        style={{
          padding: '10px 12px',
          borderBottom: '1px solid rgba(0, 255, 255, 0.12)',
          background: 'rgba(0, 20, 40, 0.6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Brain style={{ width: 14, height: 14, color: '#00e5ff' }} />
            <span
              style={{
                fontFamily: "'Orbitron', 'Share Tech Mono', monospace",
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: '0.18em',
                color: '#e0f7fa',
                textTransform: 'uppercase',
              }}
            >
              MEMORY MATRIX
            </span>
          </div>
          <span
            style={{
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 9,
              letterSpacing: '0.12em',
              color: 'rgba(0, 229, 255, 0.5)',
              marginLeft: 22,
              textTransform: 'uppercase',
            }}
          >
            PERSISTENT KNOWLEDGE ARCHIVE
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Status indicator */}
          <span
            style={{
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 9,
              letterSpacing: '0.1em',
              color: '#00e5ff',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: '#00e5ff',
                boxShadow: '0 0 6px #00e5ff',
                display: 'inline-block',
                animation: 'pulse 2s ease-in-out infinite',
              }}
            />
            MEMORY ONLINE
          </span>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            title="Add Memory Fact"
            style={{
              background: 'rgba(0, 229, 255, 0.08)',
              border: '1px solid rgba(0, 229, 255, 0.3)',
              borderRadius: 3,
              padding: '3px 6px',
              color: '#00e5ff',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(0, 229, 255, 0.18)';
              (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 8px rgba(0,229,255,0.3)';
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.background = 'rgba(0, 229, 255, 0.08)';
              (e.currentTarget as HTMLButtonElement).style.boxShadow = 'none';
            }}
          >
            <Plus style={{ width: 13, height: 13 }} />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              title="Close Panel"
              style={{
                background: 'transparent',
                border: 'none',
                color: 'rgba(0, 229, 255, 0.4)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                padding: 3,
                borderRadius: 3,
                transition: 'color 0.15s',
              }}
              onMouseEnter={e => ((e.currentTarget as HTMLButtonElement).style.color = '#fff')}
              onMouseLeave={e => ((e.currentTarget as HTMLButtonElement).style.color = 'rgba(0,229,255,0.4)')}
            >
              <X style={{ width: 14, height: 14 }} />
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <div style={{ padding: '8px 10px', borderBottom: '1px solid rgba(0, 255, 255, 0.07)' }}>
        <div style={{ position: 'relative' }}>
          <Search
            style={{
              width: 12,
              height: 12,
              position: 'absolute',
              left: 9,
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'rgba(0, 229, 255, 0.45)',
              pointerEvents: 'none',
            }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="SEARCH MEMORY ARCHIVE..."
            style={{
              width: '100%',
              background: 'rgba(0, 10, 25, 0.8)',
              border: '1px solid rgba(0, 229, 255, 0.2)',
              borderRadius: 3,
              paddingLeft: 28,
              paddingRight: 10,
              paddingTop: 6,
              paddingBottom: 6,
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 10,
              color: '#b2ebf2',
              outline: 'none',
              letterSpacing: '0.08em',
              boxSizing: 'border-box',
              transition: 'border-color 0.15s, box-shadow 0.15s',
            }}
            onFocus={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.6)';
              e.currentTarget.style.boxShadow = '0 0 10px rgba(0,229,255,0.15)';
            }}
            onBlur={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
        </div>
      </div>

      {/* Add Memory Form */}
      {showAddForm && (
        <form
          onSubmit={handleAddSubmit}
          style={{
            padding: '10px 12px',
            background: 'rgba(0, 20, 50, 0.7)',
            borderBottom: '1px solid rgba(0, 229, 255, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            gap: 7,
          }}
        >
          <div style={{
            fontFamily: "'Share Tech Mono', monospace",
            fontSize: 9,
            letterSpacing: '0.14em',
            color: 'rgba(0,229,255,0.6)',
            marginBottom: 2,
            textTransform: 'uppercase',
          }}>
            ▸ INJECT MEMORY NODE
          </div>
          <input
            type="text"
            placeholder="MEMORY KEY (e.g. preferred_editor)"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            style={{
              background: 'rgba(0, 5, 18, 0.9)',
              border: '1px solid rgba(0, 229, 255, 0.2)',
              borderRadius: 3,
              padding: '6px 8px',
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 10,
              color: '#b2ebf2',
              outline: 'none',
              letterSpacing: '0.06em',
            }}
            onFocus={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.55)';
              e.currentTarget.style.boxShadow = '0 0 8px rgba(0,229,255,0.12)';
            }}
            onBlur={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
          <input
            type="text"
            placeholder="VALUE (e.g. VS Code)"
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            style={{
              background: 'rgba(0, 5, 18, 0.9)',
              border: '1px solid rgba(0, 229, 255, 0.2)',
              borderRadius: 3,
              padding: '6px 8px',
              fontFamily: "'Share Tech Mono', monospace",
              fontSize: 10,
              color: '#b2ebf2',
              outline: 'none',
              letterSpacing: '0.06em',
            }}
            onFocus={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.55)';
              e.currentTarget.style.boxShadow = '0 0 8px rgba(0,229,255,0.12)';
            }}
            onBlur={e => {
              e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              style={{
                padding: '5px 12px',
                background: 'rgba(20, 30, 50, 0.8)',
                border: '1px solid rgba(100, 130, 160, 0.25)',
                borderRadius: 3,
                color: '#78909c',
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 10,
                letterSpacing: '0.08em',
                cursor: 'pointer',
                textTransform: 'uppercase',
              }}
            >
              CANCEL
            </button>
            <button
              type="submit"
              style={{
                padding: '5px 14px',
                background: 'rgba(0, 229, 255, 0.12)',
                border: '1px solid rgba(0, 229, 255, 0.5)',
                borderRadius: 3,
                color: '#00e5ff',
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 10,
                letterSpacing: '0.08em',
                cursor: 'pointer',
                fontWeight: 700,
                textTransform: 'uppercase',
                boxShadow: '0 0 8px rgba(0,229,255,0.2)',
              }}
            >
              COMMIT NODE
            </button>
          </div>
        </form>
      )}

      {/* Memory List */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '8px 10px',
          display: 'flex',
          flexDirection: 'column',
          gap: 5,
          fontFamily: "'Share Tech Mono', monospace",
          fontSize: 11,
        }}
      >
        {memories.length === 0 ? (
          <div
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'rgba(0, 229, 255, 0.25)',
              fontSize: 10,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}
          >
            NO MEMORY NODES DETECTED
          </div>
        ) : (
          memories.map((item) => (
            <div
              key={item.id}
              className="memory-entry-row"
              style={{
                background: 'rgba(0, 15, 35, 0.7)',
                border: '1px solid rgba(0, 229, 255, 0.1)',
                borderLeft: '3px solid rgba(0, 229, 255, 0.45)',
                borderRadius: '0 3px 3px 0',
                padding: '6px 8px 6px 10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                transition: 'border-color 0.15s, background 0.15s',
                position: 'relative',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(0,229,255,0.28)';
                (e.currentTarget as HTMLDivElement).style.background = 'rgba(0, 20, 50, 0.75)';
                const btn = (e.currentTarget as HTMLDivElement).querySelector('.del-btn') as HTMLElement;
                if (btn) btn.style.opacity = '1';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(0,229,255,0.1)';
                (e.currentTarget as HTMLDivElement).style.background = 'rgba(0, 15, 35, 0.7)';
                const btn = (e.currentTarget as HTMLDivElement).querySelector('.del-btn') as HTMLElement;
                if (btn) btn.style.opacity = '0';
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2, flex: 1, minWidth: 0 }}>
                <span
                  style={{
                    fontWeight: 700,
                    color: '#80deea',
                    textTransform: 'uppercase',
                    fontSize: 10,
                    letterSpacing: '0.1em',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {item.key}
                </span>
                <span
                  style={{
                    color: '#cfd8dc',
                    fontSize: 11,
                    wordBreak: 'break-word',
                  }}
                >
                  {item.value}
                </span>
                <span
                  style={{
                    fontSize: 9,
                    color: 'rgba(0, 229, 255, 0.35)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                    marginTop: 1,
                  }}
                >
                  [{item.category}]
                </span>
              </div>
              <button
                className="del-btn"
                onClick={() => onDeleteMemory(item.id)}
                title="Delete memory entry"
                style={{
                  opacity: 0,
                  background: 'transparent',
                  border: 'none',
                  color: 'rgba(239, 83, 80, 0.7)',
                  cursor: 'pointer',
                  padding: '2px 4px',
                  borderRadius: 3,
                  transition: 'opacity 0.15s, color 0.15s',
                  flexShrink: 0,
                  marginLeft: 6,
                }}
                onMouseEnter={e => ((e.currentTarget as HTMLButtonElement).style.color = '#ef5350')}
                onMouseLeave={e => ((e.currentTarget as HTMLButtonElement).style.color = 'rgba(239,83,80,0.7)')}
              >
                <Trash2 style={{ width: 12, height: 12 }} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
