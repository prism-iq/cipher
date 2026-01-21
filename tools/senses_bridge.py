"""
SENSES BRIDGE - Connexion sens -> Cipher

Le pont entre le systeme nerveux unifie (senses.py) et le cerveau cognitif (cipher_brain.py).
La musique guide la forge. L'energie module l'apprentissage.

Paradigme 140/174 BPM:
- 140 BPM = confiance (dubstep) -> apprentissage stable, reflexion
- 174 BPM = direction (neurofunk) -> apprentissage intense, cross-domain

Vibes:
- hype (energy > 0.7)  -> mode intense, plus de papers, cross-domain
- chill (energy < 0.3) -> mode reflexif, detection de patterns
- groovy (0.3-0.7)     -> mode equilibre
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LearningMode(Enum):
    """Modes d'apprentissage modules par les sens"""
    INTENSE = "intense"      # hype: max papers, cross-domain focus
    BALANCED = "balanced"    # groovy: equilibre
    REFLECTIVE = "reflective"  # chill: patterns, synthesis


@dataclass
class SensoryState:
    """Etat sensoriel actuel"""
    # Audio (musique)
    music_energy: float = 0.0
    music_groove: float = 0.0
    music_vibe: str = "silent"

    # Micro (voix/ambiance)
    mic_energy: float = 0.0
    mic_active: bool = False

    # Vision
    vision_path: Optional[str] = None
    vision_ts: Optional[str] = None

    # Screen
    screen_path: Optional[str] = None
    screen_ts: Optional[str] = None

    # Touch
    touch_x: int = 0
    touch_y: int = 0

    # Meta
    last_update: datetime = None

    def get_learning_mode(self) -> LearningMode:
        """Determine le mode d'apprentissage selon l'etat sensoriel"""
        if self.music_vibe == "hype" or self.music_energy > 0.7:
            return LearningMode.INTENSE
        elif self.music_vibe == "chill" or self.music_energy < 0.3:
            return LearningMode.REFLECTIVE
        else:
            return LearningMode.BALANCED

    def get_learning_params(self) -> Dict[str, Any]:
        """Parametres d'apprentissage selon le mode"""
        mode = self.get_learning_mode()

        if mode == LearningMode.INTENSE:
            return {
                "max_papers": 50,
                "cross_domain_ratio": 0.6,  # 60% cross-domain
                "pattern_detection_interval": 100,  # tous les 100 papers
                "parallel_learning": True,
                "domains_per_cycle": 3,
            }
        elif mode == LearningMode.REFLECTIVE:
            return {
                "max_papers": 10,
                "cross_domain_ratio": 0.2,
                "pattern_detection_interval": 20,
                "parallel_learning": False,
                "domains_per_cycle": 1,
                "run_synthesis": True,  # genere rapport
            }
        else:  # BALANCED
            return {
                "max_papers": 25,
                "cross_domain_ratio": 0.4,
                "pattern_detection_interval": 50,
                "parallel_learning": True,
                "domains_per_cycle": 2,
            }


class SensesBridge:
    """
    Pont entre senses.py et cipher_brain.py

    Surveille les fichiers JSON sensoriels et adapte le comportement de Cipher.
    """

    def __init__(self, cipher_path: Path = None):
        self.cipher_path = cipher_path or Path.home() / "projects" / "cipher"
        self.state = SensoryState()
        self.running = False
        self._callbacks: Dict[str, Callable] = {}
        self._last_mode: Optional[LearningMode] = None

    def read_sense(self, sense: str) -> Optional[Dict]:
        """Lit un fichier sensoriel JSON"""
        path = self.cipher_path / f"{sense}.json"
        try:
            if path.exists():
                return json.loads(path.read_text())
        except (json.JSONDecodeError, IOError) as e:
            logger.debug(f"Cannot read {sense}.json: {e}")
        return None

    def update_state(self):
        """Met a jour l'etat sensoriel depuis les fichiers JSON"""
        # Music
        music = self.read_sense("music")
        if music:
            self.state.music_energy = music.get("energy", 0.0)
            self.state.music_groove = music.get("groove", 0.0)
            self.state.music_vibe = music.get("vibe", "silent")

        # Mic
        mic = self.read_sense("mic")
        if mic:
            self.state.mic_energy = mic.get("energy", 0.0)
            self.state.mic_active = mic.get("energy", 0) > 0.05

        # Vision
        vision = self.read_sense("vision")
        if vision:
            self.state.vision_path = vision.get("path")
            self.state.vision_ts = vision.get("ts")

        # Screen
        screen = self.read_sense("screen")
        if screen:
            self.state.screen_path = screen.get("path")
            self.state.screen_ts = screen.get("ts")

        # Touch
        touch = self.read_sense("touch")
        if touch:
            self.state.touch_x = touch.get("x", 0)
            self.state.touch_y = touch.get("y", 0)

        self.state.last_update = datetime.now()

    def on_mode_change(self, callback: Callable[[LearningMode, LearningMode], None]):
        """Register callback for mode changes"""
        self._callbacks['mode_change'] = callback

    def on_sense_update(self, callback: Callable[[SensoryState], None]):
        """Register callback for any sensory update"""
        self._callbacks['sense_update'] = callback

    async def watch(self, interval: float = 0.5):
        """
        Boucle de surveillance des sens.
        Met a jour l'etat et declenche les callbacks.
        """
        self.running = True
        logger.info(f"SensesBridge watching {self.cipher_path}")

        while self.running:
            try:
                self.update_state()

                # Trigger sense update callback
                if 'sense_update' in self._callbacks:
                    try:
                        self._callbacks['sense_update'](self.state)
                    except Exception as e:
                        logger.error(f"Sense update callback error: {e}")

                # Check for mode change
                current_mode = self.state.get_learning_mode()
                if current_mode != self._last_mode:
                    if self._last_mode is not None:
                        logger.info(f"Mode change: {self._last_mode.value} -> {current_mode.value}")
                        if 'mode_change' in self._callbacks:
                            try:
                                self._callbacks['mode_change'](self._last_mode, current_mode)
                            except Exception as e:
                                logger.error(f"Mode change callback error: {e}")
                    self._last_mode = current_mode

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                await asyncio.sleep(1)

        logger.info("SensesBridge stopped")

    def stop(self):
        """Stop watching"""
        self.running = False

    def get_status(self) -> Dict[str, Any]:
        """Get current sensory status for display"""
        return {
            "mode": self.state.get_learning_mode().value,
            "music": {
                "energy": self.state.music_energy,
                "groove": self.state.music_groove,
                "vibe": self.state.music_vibe,
            },
            "mic_active": self.state.mic_active,
            "has_vision": self.state.vision_path is not None,
            "has_screen": self.state.screen_path is not None,
            "last_update": self.state.last_update.isoformat() if self.state.last_update else None,
        }


async def sensory_learning_loop(
    brain,  # CipherBrain instance
    learner,  # DomainLearner instance
    bridge: SensesBridge,
    domains: list = None
):
    """
    Boucle d'apprentissage modulee par les sens.

    La musique guide la forge:
    - hype -> apprentissage intense
    - chill -> reflexion et synthese
    - groovy -> equilibre
    """
    from tools.cipher_brain import Domain

    if domains is None:
        domains = [Domain.NEUROSCIENCES, Domain.BIOLOGY, Domain.PSYCHOLOGY]

    logger.info("Sensory learning loop started")

    papers_since_pattern = 0

    while bridge.running:
        try:
            # Get current learning params from sensory state
            bridge.update_state()
            params = bridge.state.get_learning_params()
            mode = bridge.state.get_learning_mode()

            logger.info(f"Learning mode: {mode.value} | Energy: {bridge.state.music_energy:.2f} | Vibe: {bridge.state.music_vibe}")

            # REFLECTIVE mode: focus on patterns and synthesis
            if mode == LearningMode.REFLECTIVE:
                if params.get("run_synthesis"):
                    logger.info("Reflective mode: running pattern detection")
                    # Import here to avoid circular
                    from tools.pattern_detector import PatternDetector
                    from config.settings import config

                    detector = PatternDetector(config.db.connection_string)
                    await detector.connect()
                    insights = await detector.detect_all_patterns()
                    await detector.save_insights(insights)
                    await detector.close()

                    logger.info(f"Detected {len(insights)} cross-domain insights")

                # Learn slowly
                for domain in domains[:params["domains_per_cycle"]]:
                    await learner.learn_domain(domain, max_papers=params["max_papers"])
                    papers_since_pattern += params["max_papers"]

            # INTENSE mode: fast parallel learning
            elif mode == LearningMode.INTENSE:
                logger.info("Intense mode: parallel cross-domain learning")

                if params["parallel_learning"]:
                    sessions = await learner.learn_all_domains(
                        max_papers_per_domain=params["max_papers"],
                        parallel=True
                    )
                    papers_since_pattern += sum(s.papers_fetched for s in sessions if s)
                else:
                    for domain in domains[:params["domains_per_cycle"]]:
                        session = await learner.learn_domain(domain, max_papers=params["max_papers"])
                        papers_since_pattern += session.papers_fetched

            # BALANCED mode
            else:
                logger.info("Balanced mode: steady learning")
                for domain in domains[:params["domains_per_cycle"]]:
                    session = await learner.learn_domain(domain, max_papers=params["max_papers"])
                    papers_since_pattern += session.papers_fetched

            # Run pattern detection periodically
            if papers_since_pattern >= params["pattern_detection_interval"]:
                logger.info(f"Running pattern detection ({papers_since_pattern} papers since last)")
                from tools.pattern_detector import PatternDetector
                from config.settings import config

                detector = PatternDetector(config.db.connection_string)
                await detector.connect()
                insights = await detector.detect_all_patterns()
                await detector.save_insights(insights)
                await detector.close()

                papers_since_pattern = 0

            # Brief pause between cycles
            await asyncio.sleep(5)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Sensory learning error: {e}")
            await asyncio.sleep(10)

    logger.info("Sensory learning loop stopped")


# CLI for testing
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    bridge = SensesBridge()
    bridge.update_state()

    status = bridge.get_status()
    print(f"\n=== CIPHER SENSES ===")
    print(f"Mode: {status['mode']}")
    print(f"Music: energy={status['music']['energy']:.2f}, groove={status['music']['groove']:.2f}, vibe={status['music']['vibe']}")
    print(f"Mic active: {status['mic_active']}")
    print(f"Vision: {'yes' if status['has_vision'] else 'no'}")
    print(f"Screen: {'yes' if status['has_screen'] else 'no'}")

    params = bridge.state.get_learning_params()
    print(f"\n=== LEARNING PARAMS ===")
    for k, v in params.items():
        print(f"  {k}: {v}")

    if "--watch" in sys.argv:
        print("\nWatching... (Ctrl+C to stop)")
        try:
            asyncio.run(bridge.watch(interval=1.0))
        except KeyboardInterrupt:
            bridge.stop()
