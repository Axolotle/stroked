from defcon import LayerSet as DLayerSet


class LayerSet(DLayerSet):
    def _layerNameChange(self, notification):
        data = notification.data
        oldName = data["oldName"]
        newName = data["newName"]
        self._layers[newName] = self._layers.pop(oldName)
        index = self._layerOrder.index(oldName)
        self._layerOrder.pop(index)
        self._layerOrder.insert(index, newName)
        self._layerActionHistory.append(
            dict(action="rename", oldName=oldName, newName=newName))
        self.postNotification("LayerSet.LayerNameChanged",
                              data=dict(oldName=oldName, newName=newName))
