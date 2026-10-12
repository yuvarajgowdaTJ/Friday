import React, { useEffect, useRef, useMemo } from 'react';
import { Mic, Cpu, Volume2, Zap, AlertTriangle, Activity } from 'lucide-react';
import type { AssistantState } from './AIReactor';

interface HolographicCoreProps {
  state: AssistantState;
  statusText?: string;
  activeToolName?: string | null;
  wakeDetected?: boolean;
}

interface Point3D {
  x: number;
  y: number;
  z: number;
  baseX: number;
  baseY: number;
  baseZ: number;
}

export const HolographicCore: React.FC<HolographicCoreProps> = ({
  state,
  statusText,
  activeToolName,
  wakeDetected
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // State-specific futuristic cyan/blue visual parameters
  const theme = useMemo(() => {
    switch (state) {
      case 'LISTENING':
        return {
          coreColor: '#00F3FF',       // Electric cyan
          glowColor: '#38BDF8',       // Neon blue
          accentColor: '#E0F2FE',     // Soft white / ice
          speed: 1.5,
          pulseSpeed: 2.2,
          label: 'VOICE RECEPTOR ACTIVE',
          subtext: 'CAPTURING CONTINUOUS SPEECH AUDIO',
          icon: Mic,
          particleGlow: 'rgba(0, 243, 255, 0.95)',
          neuralAlpha: 0.35,
          radarActive: true,
          ringSpeed: '10s'
        };
      case 'THINKING':
        return {
          coreColor: '#38BDF8',       // Neon blue
          glowColor: '#00F3FF',       // Electric cyan
          accentColor: '#7DD3FC',     // Ice blue
          speed: 2.6,
          pulseSpeed: 3.4,
          label: 'NEURAL PROCESSING',
          subtext: 'ROUTING INTENTS & COGNITIVE ENGINES',
          icon: Cpu,
          particleGlow: 'rgba(56, 189, 248, 0.95)',
          neuralAlpha: 0.55,
          radarActive: true,
          ringSpeed: '6s'
        };
      case 'SPEAKING':
        return {
          coreColor: '#00F3FF',       // Electric cyan
          glowColor: '#7DD3FC',       // Ice blue
          accentColor: '#FFFFFF',     // Brilliant white
          speed: 1.6,
          pulseSpeed: 2.6,
          label: 'VOCAL SYNTHESIS',
          subtext: 'TRANSMITTING NATURAL CONVERSATIONAL SPEECH',
          icon: Volume2,
          particleGlow: 'rgba(224, 242, 254, 1.0)',
          neuralAlpha: 0.3,
          radarActive: false,
          ringSpeed: '12s'
        };
      case 'EXECUTING':
        return {
          coreColor: '#0284c7',       // Deep electric blue
          glowColor: '#00F3FF',       // Cyan
          accentColor: '#38BDF8',     // Neon blue
          speed: 2.0,
          pulseSpeed: 2.8,
          label: 'SUBSYSTEM DIRECTIVE',
          subtext: `EXECUTING: ${activeToolName ? activeToolName.toUpperCase() : 'SYSTEM FUNCTION'}`,
          icon: Zap,
          particleGlow: 'rgba(0, 243, 255, 0.95)',
          neuralAlpha: 0.45,
          radarActive: false,
          ringSpeed: '8s'
        };
      case 'ERROR':
        return {
          coreColor: '#ef4444',       // Restrained red warning
          glowColor: '#f87171',
          accentColor: '#991b1b',
          speed: 0.6,
          pulseSpeed: 1.0,
          label: 'DIAGNOSTIC EVENT',
          subtext: 'ANOMALY DETECTED IN PIPELINE',
          icon: AlertTriangle,
          particleGlow: 'rgba(248, 113, 113, 0.85)',
          neuralAlpha: 0.2,
          radarActive: false,
          ringSpeed: '24s'
        };
      case 'IDLE':
      default:
        return {
          coreColor: '#0ea5e9',       // Calm sky blue
          glowColor: '#00F3FF',       // Electric cyan
          accentColor: '#7DD3FC',     // Ice blue
          speed: 0.7,
          pulseSpeed: 1.0,
          label: 'STANDBY',
          subtext: 'QUANTUM CORE NOMINAL — READY FOR DIRECTIVE',
          icon: Activity,
          particleGlow: 'rgba(0, 243, 255, 0.8)',
          neuralAlpha: 0.2,
          radarActive: false,
          ringSpeed: '20s'
        };
    }
  }, [state, activeToolName]);

  // Canvas 3D Holographic Particle Sphere & Neural Lattice Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let angleY = 0;
    let angleX = 0.22;
    let pulseTime = 0;

    const SPHERE_RADIUS = 92;
    const NUM_LATITUDE = 12;
    const NUM_LONGITUDE = 18;
    const points: Point3D[] = [];
    const neuralEdges: [number, number][] = [];

    // 1. Generate 3D sphere surface vertices
    for (let i = 0; i <= NUM_LATITUDE; i++) {
      const theta = (i * Math.PI) / NUM_LATITUDE;
      const sinTheta = Math.sin(theta);
      const cosTheta = Math.cos(theta);

      for (let j = 0; j < NUM_LONGITUDE; j++) {
        const phi = (j * 2 * Math.PI) / NUM_LONGITUDE;
        const x = SPHERE_RADIUS * sinTheta * Math.cos(phi);
        const y = SPHERE_RADIUS * cosTheta;
        const z = SPHERE_RADIUS * sinTheta * Math.sin(phi);

        const currentIdx = points.length;
        points.push({ x, y, z, baseX: x, baseY: y, baseZ: z });

        // Connect adjacent points on latitude & longitude for neural lattice
        if (j > 0) {
          neuralEdges.push([currentIdx, currentIdx - 1]);
        } else if (NUM_LONGITUDE > 1) {
          neuralEdges.push([currentIdx, currentIdx + NUM_LONGITUDE - 1]);
        }
        if (i > 0) {
          neuralEdges.push([currentIdx, currentIdx - NUM_LONGITUDE]);
        }
        // Diagonal cross-links for neural topology (every 3rd node)
        if (i > 0 && j % 3 === 0) {
          neuralEdges.push([currentIdx, (currentIdx - NUM_LONGITUDE - 1 + points.length) % points.length]);
        }
      }
    }

    // 2. Ambient holographic particles floating around the sphere
    const ambientParticles = Array.from({ length: 44 }, () => ({
      x: (Math.random() - 0.5) * 270,
      y: (Math.random() - 0.5) * 270,
      z: (Math.random() - 0.5) * 270,
      radius: Math.random() * 1.4 + 0.6,
      speed: Math.random() * 0.015 + 0.005,
      offset: Math.random() * Math.PI * 2,
      isHighlight: Math.random() > 0.8
    }));

    const render = (timestamp: number) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      // Dynamic rotation speed based on state
      angleY += 0.005 * theme.speed;
      angleX = Math.sin(timestamp * 0.0006) * 0.18 + 0.12;
      pulseTime = timestamp * 0.003 * theme.pulseSpeed;

      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);
      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);

      // State-based breathing & audio wave expansion factor
      const pulseFactor = state === 'SPEAKING'
        ? 1.0 + Math.sin(pulseTime * 2.2) * 0.08 + Math.cos(pulseTime * 3.8) * 0.04
        : state === 'LISTENING'
        ? 1.0 + Math.sin(pulseTime * 1.8) * 0.045
        : state === 'THINKING'
        ? 1.0 + Math.sin(pulseTime * 2.4) * 0.035
        : 1.0 + Math.sin(pulseTime * 0.8) * 0.025;

      // ── Layer 1: Concentrated Luminous Energy Singularity (Core Flare) ───────
      const coreRadius = (state === 'SPEAKING' ? 62 : 54) * pulseFactor;
      const coreGrad = ctx.createRadialGradient(
        centerX, centerY, 2,
        centerX, centerY, coreRadius
      );
      coreGrad.addColorStop(0, '#FFFFFF');
      coreGrad.addColorStop(0.18, theme.accentColor);
      coreGrad.addColorStop(0.45, theme.glowColor + '99');
      coreGrad.addColorStop(0.75, theme.coreColor + '33');
      coreGrad.addColorStop(1, 'transparent');

      ctx.fillStyle = coreGrad;
      ctx.beginPath();
      ctx.arc(centerX, centerY, coreRadius, 0, Math.PI * 2);
      ctx.fill();

      // ── Layer 2: 3D Projection of Sphere Points ─────────────────────────────
      const cameraDistance = 330;
      const projected = points.map(pt => {
        const px = pt.baseX * pulseFactor;
        const py = pt.baseY * pulseFactor;
        const pz = pt.baseZ * pulseFactor;

        // Rotate around Y axis
        const x1 = px * cosY - pz * sinY;
        const z1 = px * sinY + pz * cosY;

        // Rotate around X axis
        const y2 = py * cosX - z1 * sinX;
        const z2 = py * sinX + z1 * cosX;

        // Perspective projection
        const perspective = cameraDistance / (cameraDistance + z2);
        const screenX = centerX + x1 * perspective;
        const screenY = centerY + y2 * perspective;

        return {
          screenX,
          screenY,
          depth: z2,
          perspective,
          alpha: Math.max(0.1, (z2 + SPHERE_RADIUS) / (SPHERE_RADIUS * 2))
        };
      });

      // ── Layer 3: Neural Network Synaptic Connections ────────────────────────
      ctx.lineWidth = 0.55;
      ctx.strokeStyle = theme.glowColor;
      const baseNeuralAlpha = theme.neuralAlpha;

      for (let e = 0; e < neuralEdges.length; e++) {
        const [iA, iB] = neuralEdges[e];
        const pA = projected[iA];
        const pB = projected[iB];
        if (pA && pB) {
          // Render links when at least one node is facing forward
          if (pA.depth > -35 || pB.depth > -35) {
            const edgeAlpha = Math.min(pA.alpha, pB.alpha) * baseNeuralAlpha;
            if (edgeAlpha > 0.04) {
              ctx.globalAlpha = edgeAlpha;
              ctx.beginPath();
              ctx.moveTo(pA.screenX, pA.screenY);
              ctx.lineTo(pB.screenX, pB.screenY);
              ctx.stroke();
            }
          }
        }
      }
      ctx.globalAlpha = 1.0;

      // ── Layer 4: Latitude Wireframe Geometric Rings ─────────────────────────
      ctx.strokeStyle = theme.coreColor;
      ctx.lineWidth = 0.6;
      for (let i = 1; i < NUM_LATITUDE; i++) {
        ctx.beginPath();
        let started = false;
        for (let j = 0; j <= NUM_LONGITUDE; j++) {
          const idx = i * NUM_LONGITUDE + (j % NUM_LONGITUDE);
          const p = projected[idx];
          if (p && p.depth > -40) {
            ctx.globalAlpha = p.alpha * 0.22;
            if (!started) {
              ctx.moveTo(p.screenX, p.screenY);
              started = true;
            } else {
              ctx.lineTo(p.screenX, p.screenY);
            }
          }
        }
        ctx.stroke();
      }
      ctx.globalAlpha = 1.0;

      // ── Layer 5: Luminous Nodes on Sphere Surface ────────────────────────────
      for (let i = 0; i < projected.length; i++) {
        const p = projected[i];
        if (p.depth > -70) {
          const pointRadius = Math.max(0.65, 1.85 * p.perspective);
          ctx.fillStyle = p.depth > 30 ? theme.accentColor : theme.particleGlow;
          ctx.globalAlpha = p.alpha * (p.depth > 20 ? 1.0 : 0.6);
          ctx.beginPath();
          ctx.arc(p.screenX, p.screenY, pointRadius, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      ctx.globalAlpha = 1.0;

      // ── Layer 6: Ambient Floating Holographic Particles ─────────────────────
      ambientParticles.forEach((ap, idx) => {
        const rad = timestamp * ap.speed + ap.offset;
        const ax = ap.x * Math.cos(rad) - ap.z * Math.sin(rad);
        const az = ap.x * Math.sin(rad) + ap.z * Math.cos(rad);
        const perspective = 310 / (310 + az);
        const sx = centerX + ax * perspective;
        const sy = centerY + (ap.y + Math.sin(timestamp * 0.0018 + idx) * 16) * perspective;
        const alpha = Math.max(0.08, (az + 135) / 270);

        ctx.fillStyle = ap.isHighlight ? '#E0F2FE' : theme.glowColor;
        ctx.globalAlpha = alpha * 0.65;
        ctx.beginPath();
        ctx.arc(sx, sy, ap.radius * perspective, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1.0;

      // ── Layer 7: Vocal Energy Ripples during SPEAKING ───────────────────────
      if (state === 'SPEAKING') {
        const ringCount = 3;
        for (let r = 0; r < ringCount; r++) {
          const progress = ((timestamp * 0.0018 + r / ringCount) % 1);
          const ringRadius = 65 + progress * 85;
          const ringAlpha = (1 - progress) * 0.65;

          ctx.strokeStyle = theme.glowColor;
          ctx.globalAlpha = ringAlpha;
          ctx.lineWidth = 1.4;
          ctx.beginPath();
          ctx.arc(centerX, centerY, ringRadius, 0, Math.PI * 2);
          ctx.stroke();
        }
        ctx.globalAlpha = 1.0;
      }

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animationFrameId);
  }, [state, theme]);

  const StateIcon = theme.icon;

  return (
    <div className="relative flex flex-col items-center justify-center p-3 select-none w-full h-full min-h-[380px]">
      
      {/* ── Main Holographic Viewport (Layered Concentric Orbital Rings) ───────── */}
      <div className="relative w-[350px] h-[350px] flex items-center justify-center">
        
        {/* Ring 1: Outermost Broken Arc Tech Ring (Counter-Clockwise) */}
        <div 
          className="absolute inset-0 rounded-full border border-dashed animate-spin-reverse pointer-events-none opacity-40"
          style={{ 
            borderColor: theme.coreColor,
            animationDuration: '28s'
          }}
        />

        {/* Ring 2: Precision Circular HUD with Technical Degree Ticks */}
        <div 
          className="absolute inset-3 rounded-full border border-cyan-500/20 animate-spin-slow pointer-events-none"
          style={{ animationDuration: theme.ringSpeed }}
        >
          {/* Degree Ticks */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 px-1 text-[7px] font-mono text-cyan-300/80 bg-[#000205]/80 rounded border border-cyan-500/30">
            000°
          </div>
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 px-1 text-[7px] font-mono text-cyan-300/80 bg-[#000205]/80 rounded border border-cyan-500/30">
            180°
          </div>
          <div className="absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2 px-1 text-[7px] font-mono text-cyan-300/80 bg-[#000205]/80 rounded border border-cyan-500/30">
            270°
          </div>
          <div className="absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 px-1 text-[7px] font-mono text-cyan-300/80 bg-[#000205]/80 rounded border border-cyan-500/30">
            090°
          </div>

          {/* Technical Hash Mark Accents */}
          <div className="absolute top-1/4 left-1 w-1.5 h-[1px] bg-cyan-400/50" />
          <div className="absolute top-3/4 left-1 w-1.5 h-[1px] bg-cyan-400/50" />
          <div className="absolute top-1/4 right-1 w-1.5 h-[1px] bg-cyan-400/50" />
          <div className="absolute top-3/4 right-1 w-1.5 h-[1px] bg-cyan-400/50" />
        </div>

        {/* Ring 3: Segmented SVG Orbit Path with Technical Cutouts */}
        <svg 
          className="absolute inset-6 w-[302px] h-[302px] pointer-events-none animate-spin-reverse opacity-50"
          style={{ animationDuration: '22s' }}
          viewBox="0 0 300 300"
        >
          <circle 
            cx="150" cy="150" r="146" 
            fill="none" 
            stroke={theme.glowColor} 
            strokeWidth="1" 
            strokeDasharray="18 12 4 12 36 14"
          />
          <circle 
            cx="150" cy="150" r="138" 
            fill="none" 
            stroke={theme.coreColor} 
            strokeWidth="0.75" 
            strokeDasharray="4 24 12 8" 
            opacity="0.6"
          />
        </svg>

        {/* Ring 4: Radial Scanning Radar Arc during LISTENING & THINKING */}
        {theme.radarActive && (
          <div 
            className="absolute inset-8 rounded-full animate-spin-fast pointer-events-none opacity-30"
            style={{
              background: `conic-gradient(from 0deg, transparent 65%, ${theme.coreColor} 100%)`,
              maskImage: 'radial-gradient(circle, transparent 58%, black 62%)',
              WebkitMaskImage: 'radial-gradient(circle, transparent 58%, black 62%)'
            }}
          />
        )}

        {/* Ring 5: Targeting Reticle during EXECUTING */}
        {state === 'EXECUTING' && (
          <div className="absolute inset-4 border border-cyan-400/50 rounded-full animate-ping pointer-events-none" />
        )}

        {/* Center: HTML5 Canvas 3D Particle Sphere + Neural Mesh */}
        <canvas
          ref={canvasRef}
          width={350}
          height={350}
          className="relative z-10 w-[350px] h-[350px]"
        />

        {/* Orbiting Satellite Data Nodes */}
        <div 
          className="absolute inset-2 animate-spin-slow pointer-events-none"
          style={{ animationDuration: state === 'THINKING' ? '5s' : '16s' }}
        >
          <div 
            className="absolute top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full shadow-[0_0_10px_#00F3FF]"
            style={{ backgroundColor: theme.accentColor }}
          />
          <div 
            className="absolute bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full shadow-[0_0_8px_#38BDF8]"
            style={{ backgroundColor: theme.coreColor }}
          />
        </div>
      </div>

      {/* ── Holographic System Identification & Status HUD ────────────────────── */}
      <div className="mt-2 flex flex-col items-center space-y-1.5 z-20">
        
        {/* Core System Label: F.R.I.D.A.Y */}
        <div className="flex flex-col items-center">
          <h2 className="font-display font-black text-sm tracking-[0.35em] text-cyan-100 uppercase glow-text-cyan">
            F . R . I . D . A . Y
          </h2>
          <span className="font-mono text-[8px] tracking-[0.22em] text-cyan-400/70 uppercase">
            FUTURE READY INTELLIGENT DIGITAL ASSISTANT
          </span>
        </div>

        {/* Floating Capsule Badge: Active State Indicator */}
        <div 
          className="px-3.5 py-1 rounded-full flex items-center space-x-2 border backdrop-blur-md shadow-[0_0_16px_rgba(0,243,255,0.15)] transition-all duration-300"
          style={{
            borderColor: `${theme.coreColor}55`,
            backgroundColor: 'rgba(2, 8, 23, 0.88)'
          }}
        >
          <StateIcon className="w-3.5 h-3.5 animate-pulse" style={{ color: theme.glowColor }} />
          <span className="font-display font-bold text-xs tracking-widest text-cyan-100 uppercase">
            {theme.label}
          </span>
          {activeToolName && state === 'EXECUTING' && (
            <span className="px-1.5 py-0.5 rounded bg-cyan-500/20 text-[10px] font-mono font-bold text-cyan-200 border border-cyan-400/40">
              {activeToolName.toUpperCase()}
            </span>
          )}
        </div>

        {/* Dynamic Status Readout */}
        <p className="font-mono text-xs text-cyan-300/85 tracking-wide text-center max-w-sm truncate">
          {statusText || theme.subtext}
        </p>

        {/* Wake Word Detection Alert Banner */}
        {wakeDetected && (
          <div className="mt-1 px-3 py-0.5 rounded bg-cyan-500/20 border border-cyan-400 text-cyan-200 font-mono text-[10px] tracking-wider animate-bounce shadow-[0_0_12px_rgba(0,243,255,0.3)]">
            WAKE PROTOCOL ENGAGED: "FRIDAY"
          </div>
        )}
      </div>
    </div>
  );
};
