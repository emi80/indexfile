import indexfile
from indexfile.index import Dataset

class RNADataset(Dataset):

    def __init__(self, **kwargs):
        super(RNADataset, self).__init__(**kwargs)

        self._init_attributes()

    def _init_attributes(self):
            self._attributes['primary'] = (lambda x: x.fastq[0].path if x.files.get('fastq') and len(x.fastq) > 0 else None)
            self._attributes['secondary'] = (lambda x: x.fastq[1].path if x.files.get('fastq') and len(x.fastq) > 1 else None)
            self._attributes['single_end'] = (lambda x: x.readType.upper().find('2X') == -1 if x._metadata.get('readType') else True)
            self._attributes['stranded'] = (lambda x: x.readType.upper().endswith('D') if x._metadata.get('readType') else False)


class _OnSuccessListener(object):
    def __init__(self, project, config):
        self.project = project
        self.config = config
    def __call__(self, tool, args):
        # grape.grape has an import grape.index.* so we
        # import implicitly here to avoid circular dependencies
        from .grape import Project

        project = Project(self.project)
        index = project.index
        try:
            index.lock()
            for k in tool.__dict__['outputs']:
                v = self.config[k]
                if os.path.exists(v):
                    name, ext = os.path.splitext(v)
                    if ext == '.gz':
                        name, ext = os.path.splitext(name)
                    info = {'type': ext.lstrip('.'), 'md5': utils.md5sum(v)}
                    if self.config.has_key('view') and self.config['view'].get(k, None):
                        info['view'] = self.config['view'][k]
                    index.add(self.config['name'], v, info)
            index.save()
        finally:
            index.release()

def prepare_tool(tool, project, config):
    """Add listeners to the tool to ensure that it updates the index
    during execution.

    :param tool: the tool instance
    :type tool: jip.tools.Tool
    :param project: the project
    :type project: grape.Project
    :param name: the run name used to identify the job store
    :type name: string
    """
    tool.on_success.append(_OnSuccessListener(project, config))
