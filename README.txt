
**************
*** Knodes ***
**************

Requirements:
	- Dead Simple.
	- Timestamped Data and Tags
	- Flat file db
	- Simple interfce for browsing tags
	- Simple interface for inputting knodes

Tag Syntax:
    - No tags with spaces are permited
    - Space are treated ad seperators between tags
    - Tags can be comma seperated or space seperated
    - Any string coming before :: is considered to be the name of the knode

Database Structure:
	- flat file db, using xml

	- /tags/ dir:
		* contains tag files for each tag
		* tag file contains uids for each knode

		ex: subtle_bodies.tag
            <tag name="">
    			<knode>
    				90928134
    			</knode>
    			<knode>
    				112638
    			</knode>
            </tag>

	- /knodes/
		* contains knode files for each knode

		ex: 90928134.knode

			<knode name="" knode_id="">
				<created>
				</created>
                
				<last_updated>
				</last_updated>

				<text>
				</text>

				<tag>
				</tag>

				<tag>
				</tag>
			</knode>