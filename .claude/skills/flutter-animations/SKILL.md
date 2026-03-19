---
name: flutter-animations
description: "Flutter animation implementation guide covering implicit, explicit, hero, staggered, and physics-based animations. Use when implementing animations in Flutter apps."
---

# Flutter Animations

Comprehensive guide for Flutter animation implementation across five main categories.

## Animation Decision Tree

Select the appropriate animation approach:

- **Implicit Animations**: Automatically handle property changes without controllers (AnimatedContainer, AnimatedOpacity, TweenAnimationBuilder). Best for simple state-driven effects.
- **Explicit Animations**: Provide full lifecycle control via AnimationController for complex scenarios.
- **Hero Animations**: Enable shared element transitions between screens.
- **Staggered Animations**: Coordinate multiple animations with sequential or overlapping timing.
- **Physics-Based Animations**: Use simulations for natural, lifelike motion.

## Key Implementation Patterns

Implicit animations automatically handle the animation when properties change. No controller needed, making them ideal for simple state-driven effects.

For advanced scenarios, the **AnimatedBuilder** pattern is best for complex widgets with animations, offering performance benefits over setState-based approaches.

## Best Practices

- Always dispose AnimationController to prevent memory leaks
- Prefer AnimatedBuilder over setState in animation listeners
- Use appropriate curves from the Curves class for natural motion
- Leverage timeDilation for debugging animation timing
- Respect user accessibility preferences regarding motion

## References

- `references/implicit.md` — Implicit animation patterns
- `references/explicit.md` — Explicit animation with controllers
- `references/hero.md` — Hero transition patterns
- `references/staggered.md` — Staggered animation coordination
- `references/physics.md` — Physics-based animations
- `references/curves.md` — Animation curves reference
