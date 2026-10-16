"use client";

class SpatialAudioEngine {
  private ctx: AudioContext | null = null;
  private muted = false;

  constructor() {
    if (typeof window !== "undefined") {
      this.muted =
        window.localStorage.getItem("proptech_audio_muted") === "true";
    }
  }

  public isMuted(): boolean {
    return this.muted;
  }

  public toggleMute(): boolean {
    this.muted = !this.muted;
    if (typeof window !== "undefined") {
      window.localStorage.setItem("proptech_audio_muted", String(this.muted));
    }
    return this.muted;
  }

  private getContext(): AudioContext | null {
    if (typeof window === "undefined" || this.muted) return null;
    if (!this.ctx) {
      const AudioCtx =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext })
          .webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    return this.ctx;
  }

  /**
   * Play a 3D spatialized chime using PannerNode + BiquadFilterNode.
   * panX: -1.0 (left) to +1.0 (right)
   */
  public playSpatialCue(
    type: "AGENT_DONE" | "HITL_WARNING" | "DEAL_SHARED",
    panX = 0.2
  ): void {
    const ctx = this.getContext();
    if (!ctx) return;

    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const filter = ctx.createBiquadFilter();
      const panner = ctx.createPanner();
      const gain = ctx.createGain();

      panner.panningModel = "equalpower";
      panner.setPosition(panX, 0, 1 - Math.abs(panX));

      filter.type = "lowpass";
      filter.frequency.setValueAtTime(1800, now);

      if (type === "AGENT_DONE") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(587.33, now); // D5
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.18); // A5
      } else if (type === "HITL_WARNING") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(311.13, now + 0.26);
      } else {
        osc.type = "sine";
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.exponentialRampToValueAtTime(1046.5, now + 0.22); // C6
      }

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.exponentialRampToValueAtTime(0.08, now + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.28);

      osc.connect(filter);
      filter.connect(panner);
      panner.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.3);
    } catch {
      // Ignore autoplay restrictions prior to user gesture
    }
  }
}

export const spatialAudio = new SpatialAudioEngine();
