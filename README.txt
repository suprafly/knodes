
**************
*** Knodes ***
**************

Requirements:
	- Dead Simple.
	- Timestamped Data and Tags
	- Flat file db
	- Simple interfce for browsing tags
	- Simple interface for inputting knodes

Database Structure:
	- flat file db, using xml

	- /tags/ dir:
		* contains tag files for each tag
		* tag file contains uids for each knode

		ex: subtle_bodies.tag

			<knode>
				90928134
			</knode>
			<knode>
				112638
			</knode>

	- /knodes/
		* contains knode files for each knode

		ex: 90928134.knode

			<knode>
				<created>
					(time in unix standard)
				</created>

				<last_updated>
				</last_updated>

				<name>
					Etheric Body
				</name>

				<text>
					The energetic body
				</text>

				<tag>
					subtle_bodies
				</tag>
				<tag>
					clairvision
				</tag>
			</knode>