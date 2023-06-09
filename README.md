# Training Song

## Description

Plays a Billboard Number 1 song corresponding to how accurate your ML model is.

## How to use

Once you've trained your model call training_song on your final accuracy result as follows:

```python
import training_song as ts

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
accuracy = ts(accuracy_score(y_test, y_pred))

>> #TODO: Insert output here
```
