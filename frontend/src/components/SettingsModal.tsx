import React, { useState } from 'react';
import { Settings as SettingsIcon, X, Key, Shield, Volume2, Save, RefreshCw, Radio } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentSettings: {
    openai_api_key_masked: string;
    openai_model: string;
    enable_voice: boolean;
    safe_mode: boolean;
    voice_continuous?: boolean;
    voice_wakeword_only?: boolean;
  };
  onSave: (newSettings: {
    apiKey?: string;
    model?: string;
    voice?: boolean;
    safeMode?: boolean;
    voiceContinuous?: boolean;
    voiceWakewordOnly?: boolean;
  }) => void;
}

// Shared input style
const inputStyle: React.CSSProperties = {
  width: '100%',
  background: 'rgba(0, 8, 22, 0.9)',
  border: '1px solid rgba(0, 229, 255, 0.2)',
  borderRadius: 3,
  padding: '7px 10px',
  fontFamily: "'Share Tech Mono', monospace",
  fontSize: 11,
  color: '#b2ebf2',
  outline: 'none',
  letterSpacing: '0.06em',
  boxSizing: 'border-box' as const,
  transition: 'border-color 0.15s, box-shadow 0.15s',
};

const sectionLabelStyle: React.CSSProperties = {
  fontFamily: "'Share Tech Mono', monospace",
  fontSize: 9,
  letterSpacing: '0.18em',
  color: 'rgba(0, 229, 255, 0.5)',
  textTransform: 'uppercase' as const,
  display: 'flex',
  alignItems: 'center',
  gap: 6,
  marginBottom: 8,
};

const dividerStyle: React.CSSProperties = {
  border: 'none',
  borderTop: '1px solid rgba(0, 229, 255, 0.07)',
  margin: '14px 0',
};

const toggleRowStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '8px 12px',
  background: 'rgba(0, 12, 30, 0.7)',
  border: '1px solid rgba(0, 229, 255, 0.1)',
  borderLeft: '3px solid rgba(0, 229, 255, 0.3)',
  borderRadius: '0 3px 3px 0',
};

function FocusInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{ ...inputStyle, ...props.style }}
      onFocus={e => {
        e.currentTarget.style.borderColor = 'rgba(0,229,255,0.55)';
        e.currentTarget.style.boxShadow = '0 0 10px rgba(0,229,255,0.13)';
        props.onFocus?.(e);
      }}
      onBlur={e => {
        e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
        e.currentTarget.style.boxShadow = 'none';
        props.onBlur?.(e);
      }}
    />
  );
}

function FocusSelect(props: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      style={{
        ...inputStyle,
        appearance: 'none' as const,
        cursor: 'pointer',
        ...props.style,
      }}
      onFocus={e => {
        e.currentTarget.style.borderColor = 'rgba(0,229,255,0.55)';
        e.currentTarget.style.boxShadow = '0 0 10px rgba(0,229,255,0.13)';
        props.onFocus?.(e);
      }}
      onBlur={e => {
        e.currentTarget.style.borderColor = 'rgba(0,229,255,0.2)';
        e.currentTarget.style.boxShadow = 'none';
        props.onBlur?.(e);
      }}
    />
  );
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  currentSettings,
  onSave,
}) => {
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState(currentSettings.openai_model || 'gpt-4o');
  const [voice, setVoice] = useState(currentSettings.enable_voice);
  const [safeMode, setSafeMode] = useState(currentSettings.safe_mode);
  const [voiceContinuous, setVoiceContinuous] = useState(currentSettings.voice_continuous ?? true);
  const [voiceWakewordOnly, setVoiceWakewordOnly] = useState(currentSettings.voice_wakeword_only ?? false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({ apiKey: apiKey.trim() ? apiKey : undefined, model, voice, safeMode, voiceContinuous, voiceWakewordOnly });
    onClose();
  };

  const toggle = (checked: boolean, setter: (v: boolean) => void) => setter(checked);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0, 0, 0, 0.88)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 16,
      }}
      className="select-none"
    >
      {/* Modal panel */}
      <div
        style={{
          width: '100%',
          maxWidth: 460,
          background: 'linear-gradient(160deg, #000000 0%, #010d20 55%, #030f28 100%)',
          border: '1px solid rgba(0, 229, 255, 0.22)',
          borderRadius: 6,
          boxShadow: '0 0 40px rgba(0, 229, 255, 0.08), 0 0 80px rgba(0, 100, 200, 0.06), inset 0 1px 0 rgba(0, 229, 255, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          gap: 0,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Corner accents */}
        <span style={{ position: 'absolute', top: 0, left: 0, width: 16, height: 16, borderTop: '1px solid rgba(0,255,255,0.55)', borderLeft: '1px solid rgba(0,255,255,0.55)', borderRadius: '3px 0 0 0', pointerEvents: 'none' }} />
        <span style={{ position: 'absolute', top: 0, right: 0, width: 16, height: 16, borderTop: '1px solid rgba(0,255,255,0.55)', borderRight: '1px solid rgba(0,255,255,0.55)', borderRadius: '0 3px 0 0', pointerEvents: 'none' }} />
        <span style={{ position: 'absolute', bottom: 0, left: 0, width: 16, height: 16, borderBottom: '1px solid rgba(0,255,255,0.55)', borderLeft: '1px solid rgba(0,255,255,0.55)', borderRadius: '0 0 0 3px', pointerEvents: 'none' }} />
        <span style={{ position: 'absolute', bottom: 0, right: 0, width: 16, height: 16, borderBottom: '1px solid rgba(0,255,255,0.55)', borderRight: '1px solid rgba(0,255,255,0.55)', borderRadius: '0 0 3px 0', pointerEvents: 'none' }} />

        {/* Header */}
        <div
          style={{
            padding: '14px 18px',
            borderBottom: '1px solid rgba(0, 229, 255, 0.12)',
            background: 'rgba(0, 20, 45, 0.6)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
              <SettingsIcon style={{ width: 15, height: 15, color: '#00e5ff' }} />
              <h3
                style={{
                  fontFamily: "'Orbitron', 'Share Tech Mono', monospace",
                  fontSize: 12,
                  fontWeight: 700,
                  letterSpacing: '0.2em',
                  color: '#e0f7fa',
                  textTransform: 'uppercase',
                  margin: 0,
                }}
              >
                FRIDAY SYSTEM CONFIGURATION
              </h3>
            </div>
            <span
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 9,
                letterSpacing: '0.14em',
                color: 'rgba(0, 229, 255, 0.45)',
                textTransform: 'uppercase',
                marginLeft: 24,
              }}
            >
              CORE SYSTEM PARAMETERS
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'rgba(0, 229, 255, 0.4)',
              cursor: 'pointer',
              padding: 4,
              borderRadius: 3,
              display: 'flex',
              alignItems: 'center',
              transition: 'color 0.15s',
            }}
            onMouseEnter={e => ((e.currentTarget as HTMLButtonElement).style.color = '#fff')}
            onMouseLeave={e => ((e.currentTarget as HTMLButtonElement).style.color = 'rgba(0,229,255,0.4)')}
          >
            <X style={{ width: 16, height: 16 }} />
          </button>
        </div>

        {/* Form body */}
        <form
          onSubmit={handleSubmit}
          style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: 0 }}
        >
          {/* ── AI MODEL ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            AI MODEL
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <FocusSelect
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            <option value="gpt-4o" style={{ background: '#010d20' }}>GPT-4o (Recommended)</option>
            <option value="gpt-4-turbo" style={{ background: '#010d20' }}>GPT-4 Turbo</option>
            <option value="gpt-3.5-turbo" style={{ background: '#010d20' }}>GPT-3.5 Turbo</option>
          </FocusSelect>

          <hr style={dividerStyle} />

          {/* ── VOICE SYSTEM ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            VOICE SYSTEM
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={toggleRowStyle}>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 11,
                  color: '#b2ebf2',
                }}
              >
                <Volume2 style={{ width: 13, height: 13, color: '#00e5ff' }} />
                SPEECH OUTPUT (TTS)
              </span>
              <input
                type="checkbox"
                checked={voice}
                onChange={(e) => toggle(e.target.checked, setVoice)}
                style={{ accentColor: '#00e5ff', width: 15, height: 15, cursor: 'pointer' }}
              />
            </div>
          </div>

          <hr style={dividerStyle} />

          {/* ── CONTINUOUS MODE ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            CONTINUOUS MODE
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={toggleRowStyle}>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 11,
                  color: '#b2ebf2',
                }}
              >
                <RefreshCw style={{ width: 13, height: 13, color: '#00e5ff' }} />
                CONTINUOUS VOICE LOOP
                <span style={{ fontSize: 9, color: 'rgba(0,229,255,0.4)', marginLeft: 2 }}>(auto-restart after command)</span>
              </span>
              <input
                type="checkbox"
                checked={voiceContinuous}
                onChange={(e) => toggle(e.target.checked, setVoiceContinuous)}
                style={{ accentColor: '#00e5ff', width: 15, height: 15, cursor: 'pointer' }}
              />
            </div>
          </div>

          <hr style={dividerStyle} />

          {/* ── WAKE WORD ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            WAKE WORD
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={toggleRowStyle}>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 11,
                  color: '#b2ebf2',
                }}
              >
                <Radio style={{ width: 13, height: 13, color: '#00e5ff' }} />
                WAKE-WORD ONLY
                <span style={{ fontSize: 9, color: 'rgba(0,229,255,0.4)', marginLeft: 2 }}>(require "FRIDAY" prefix)</span>
              </span>
              <input
                type="checkbox"
                checked={voiceWakewordOnly}
                onChange={(e) => toggle(e.target.checked, setVoiceWakewordOnly)}
                style={{ accentColor: '#00e5ff', width: 15, height: 15, cursor: 'pointer' }}
              />
            </div>
          </div>

          <hr style={dividerStyle} />

          {/* ── SECURITY ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            SECURITY
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ ...toggleRowStyle, borderLeft: '3px solid rgba(52, 211, 153, 0.35)' }}>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: "'Share Tech Mono', monospace",
                  fontSize: 11,
                  color: '#b2ebf2',
                }}
              >
                <Shield style={{ width: 13, height: 13, color: '#34d399' }} />
                SECURITY CONFIRMATION ENGINE
              </span>
              <input
                type="checkbox"
                checked={safeMode}
                onChange={(e) => toggle(e.target.checked, setSafeMode)}
                style={{ accentColor: '#34d399', width: 15, height: 15, cursor: 'pointer' }}
              />
            </div>
          </div>

          <hr style={dividerStyle} />

          {/* ── SYSTEM ── */}
          <div style={sectionLabelStyle}>
            <span style={{ display: 'inline-block', width: 14, height: 1, background: 'rgba(0,229,255,0.35)' }} />
            SYSTEM
            <span style={{ flex: 1, display: 'inline-block', height: 1, background: 'rgba(0,229,255,0.1)' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            <label
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 9,
                letterSpacing: '0.12em',
                color: 'rgba(0,229,255,0.5)',
                textTransform: 'uppercase',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                marginBottom: 4,
              }}
            >
              <Key style={{ width: 10, height: 10, color: '#00e5ff' }} />
              OPENAI API KEY
            </label>
            <FocusInput
              type="password"
              placeholder={currentSettings.openai_api_key_masked || 'ENTER sk-... API KEY'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <p
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 9,
                color: 'rgba(0,229,255,0.35)',
                letterSpacing: '0.08em',
                margin: '2px 0 0',
              }}
            >
              LEAVE BLANK TO RETAIN EXISTING KEY
            </p>
          </div>

          {/* Actions */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'flex-end',
              gap: 10,
              paddingTop: 16,
              marginTop: 4,
              borderTop: '1px solid rgba(0, 229, 255, 0.1)',
            }}
          >
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 18px',
                background: 'rgba(20, 35, 55, 0.7)',
                border: '1px solid rgba(100, 130, 160, 0.2)',
                borderRadius: 3,
                color: '#546e7a',
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 10,
                letterSpacing: '0.1em',
                cursor: 'pointer',
                textTransform: 'uppercase',
                transition: 'background 0.15s, color 0.15s',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(30, 50, 75, 0.8)';
                (e.currentTarget as HTMLButtonElement).style.color = '#90a4ae';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(20, 35, 55, 0.7)';
                (e.currentTarget as HTMLButtonElement).style.color = '#546e7a';
              }}
            >
              CANCEL
            </button>
            <button
              type="submit"
              style={{
                padding: '8px 22px',
                background: 'rgba(0, 229, 255, 0.1)',
                border: '1px solid rgba(0, 229, 255, 0.55)',
                borderRadius: 3,
                color: '#00e5ff',
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: 10,
                letterSpacing: '0.1em',
                cursor: 'pointer',
                fontWeight: 700,
                textTransform: 'uppercase',
                boxShadow: '0 0 14px rgba(0, 229, 255, 0.2)',
                display: 'flex',
                alignItems: 'center',
                gap: 7,
                transition: 'background 0.15s, box-shadow 0.15s',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(0, 229, 255, 0.18)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 22px rgba(0, 229, 255, 0.35)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLButtonElement).style.background = 'rgba(0, 229, 255, 0.1)';
                (e.currentTarget as HTMLButtonElement).style.boxShadow = '0 0 14px rgba(0, 229, 255, 0.2)';
              }}
            >
              <Save style={{ width: 13, height: 13 }} />
              SAVE CONFIGURATION
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
