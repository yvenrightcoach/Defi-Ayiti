/**
 * Effets sonores synthetises en direct via l'API Web Audio -- pas de
 * fichiers audio a heberger/precacher, tout est genere a la volee.
 * L'AudioContext n'est cree qu'au premier son joue (regle d'autoplay des
 * navigateurs : il faut un geste utilisateur, ce que garantit l'appel
 * depuis un clic/une reponse de quiz).
 */

type ToneType = OscillatorType;

interface Tone {
  freq: number;
  start: number;
  duration: number;
  type?: ToneType;
  peak?: number;
}

let ctx: AudioContext | null = null;
let enabled = true;

export function setSoundEnabled(value: boolean) {
  enabled = value;
}

function getContext(): AudioContext | null {
  if (typeof window === "undefined") return null;
  const AudioCtx = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioCtx) return null;
  if (!ctx) ctx = new AudioCtx();
  if (ctx.state === "suspended") void ctx.resume();
  return ctx;
}

function playTones(tones: Tone[]) {
  if (!enabled) return;
  const audioCtx = getContext();
  if (!audioCtx) return;
  const now = audioCtx.currentTime;

  for (const tone of tones) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = tone.type ?? "sine";
    osc.frequency.value = tone.freq;

    const startAt = now + tone.start;
    const endAt = startAt + tone.duration;
    const peak = tone.peak ?? 0.2;

    gain.gain.setValueAtTime(0, startAt);
    gain.gain.linearRampToValueAtTime(peak, startAt + Math.min(0.015, tone.duration / 4));
    gain.gain.exponentialRampToValueAtTime(0.001, endAt);

    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(startAt);
    osc.stop(endAt + 0.02);
  }
}

/** Petit clic doux, joue sur les boutons et tuiles de l'interface. */
export function playClick() {
  playTones([{ freq: 720, start: 0, duration: 0.06, type: "sine", peak: 0.12 }]);
}

/** Carillon ascendant deux notes, reponse correcte. */
export function playCorrect() {
  playTones([
    { freq: 523.25, start: 0, duration: 0.12, type: "sine", peak: 0.22 },
    { freq: 783.99, start: 0.1, duration: 0.18, type: "sine", peak: 0.2 },
  ]);
}

/** Buzz grave court, mauvaise reponse. */
export function playWrong() {
  playTones([{ freq: 160, start: 0, duration: 0.22, type: "sawtooth", peak: 0.15 }]);
}

/** Fanfare courte (3 notes), fin de niveau/match reussie. */
export function playSuccess() {
  playTones([
    { freq: 523.25, start: 0, duration: 0.13, type: "triangle", peak: 0.22 },
    { freq: 659.25, start: 0.12, duration: 0.13, type: "triangle", peak: 0.22 },
    { freq: 987.77, start: 0.24, duration: 0.3, type: "triangle", peak: 0.24 },
  ]);
}

/** Petit son "presque" doux et neutre, echec sans gravite. */
export function playSoftFail() {
  playTones([
    { freq: 392, start: 0, duration: 0.15, type: "sine", peak: 0.15 },
    { freq: 329.63, start: 0.13, duration: 0.2, type: "sine", peak: 0.15 },
  ]);
}

/** Piece/recompense, deux blips aigus rapides. */
export function playCoin() {
  playTones([
    { freq: 988, start: 0, duration: 0.06, type: "square", peak: 0.15 },
    { freq: 1319, start: 0.05, duration: 0.09, type: "square", peak: 0.15 },
  ]);
}

/** Arpege scintillant, deblocage d'un heros. */
export function playUnlock() {
  playTones([
    { freq: 659.25, start: 0, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 830.61, start: 0.08, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 1046.5, start: 0.16, duration: 0.1, type: "triangle", peak: 0.2 },
    { freq: 1318.51, start: 0.24, duration: 0.35, type: "triangle", peak: 0.24 },
  ]);
}
