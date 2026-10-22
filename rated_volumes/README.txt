36 iTELL volumes rated in the mode evaluation study (12 PDFs x 3 modes),
fetched from the iTELL CMS on 2026-10-01.

Filename: app<platform volume id>_cms<cms id>_<slug>.json
Structure: Title, Description, VolumeSummary, Pages[] -> Content[] chunks,
each chunk has Header, Text (HTML), and for page.chunk components also
Question, Answer (ConstructedResponse), KeyPhrase.

Mode and source PDF for each file (verified from content; four rows in the
rating sheet had been labelled with the wrong mode, this mapping is correct):

pdf  faithful                 simplified               condensed
008  app50                    app61                    app62
012  app63                    app64                    app65
024  app69                    app71                    app72
032  app73                    app74                    app77
050  app78                    app79                    app81
056  app82                    app83                    app84
062  app85                    app86                    app92
064  app108                   app109                   app110
077  app93                    app94                    app95
084  app96                    app97                    app98
096  app112                   app113                   app114
097  app99                    app102                   app107

Human raters saw these volumes rendered on app.itell.ai and did NOT see the
source PDF. For a comparable judge, give the model only the volume.
