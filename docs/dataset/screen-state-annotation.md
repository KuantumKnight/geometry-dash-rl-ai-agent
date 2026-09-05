# Screen-State Annotation Protocol

The detector dataset is local research material. The repository stores this
schema and the collection/evaluation metadata format, but does not store
Geometry Dash screenshots or video unless publication rights are explicitly
confirmed.

## Record format

Each captured frame has one JSON record validated by
`schemas/screen-state-annotation.schema.json`. The required fields
identify the frame, episode, UTC capture time, canonical state, level,
client resolution, window mode, visual theme effects, dataset split, and the
local image path. Optional annotator, confidence, and notes fields preserve
labeling context.

The `state` value must use the canonical state names from
`geometry_dash_env.state_machine.ScreenState`. Theme effects are
free-form tags such as `bright_green`, `dark_overlay`, or
`high_contrast`; they are not inferred from the label.

## Episode and split rules

`episode_id` is the grouping key. All frames from one episode,
including transition frames, must remain in exactly one split. Development
and held-out data are selected by episode, never by neighboring frame, so
near-duplicate frames cannot leak across the evaluation boundary.

An episode manifest records the capture configuration, source media path,
level, client resolutions and window positions used, annotation version,
annotator pass, and the selected split. A later relabeling pass creates a
new manifest version rather than editing the prior record in place.

## Publication boundary

Screenshots and videos remain untracked by default because game footage can
contain copyrighted game content, personal desktop content, or identifying
window paths. Before any sample is published, record a rights/privacy
decision in the media log. When publication is not cleared, publish only
this schema, collection scripts, aggregate metrics, and redacted metadata.
