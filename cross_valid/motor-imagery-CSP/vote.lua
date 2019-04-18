
function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	output_filename = box:get_setting(2)

	box:log("Info", string.format("Writing %s\n", output_filename))
		
	result_file = io.open(output_filename, "w")
	if result_file == nil then
		box:log("Error", "Could not open config file for writing")
	end
	lista = {}
	target = 0
	targetTime = 0
	
end

function uninitialize(box)

	result_file:write(string.format("%s,%s,", targetTime, target))
	maxSum = 0
	maxId = 0
	totalSum = 0
	for key,value in pairs(lista) do
		if(value > maxSum) then
			maxSum = value
			maxId = key
		end
		totalSum = totalSum + value
	end
	result_file:write(string.format("%s,%s,%s\n", maxId,maxSum,totalSum))		
	lista = {}
				
	box:log("Info", string.format("Vote result: Class %s, %s/%s votes for %ss", maxId, maxSum, totalSum, targetTime))	
	
	box:log("Info", string.format("END reached"))
	
	result_file:close()

end

function process(box)

	while box:keep_processing() do
	
		-- we have a new target
		for stimulation = 1, box:get_stimulation_count(1) do	

			-- vote for previous target
			if(target ~= 0) then
				result_file:write(string.format("%s,%s,", targetTime, target))
				maxSum = 0
				maxId = 0
				totalSum = 0
				for key,value in pairs(lista) do
					if(value > maxSum) then
						maxSum = value
						maxId = key
					end
					totalSum = totalSum + value
				end
				result_file:write(string.format("%s,%s,%s\n", maxId,maxSum,totalSum))		
				lista = {}
				box:log("Info", string.format("Vote result: Class %s, %s/%s votes for %ss", maxId, maxSum, totalSum, targetTime))	
			end	

			-- gets the received stimulation
			identifier, date, duration = box:get_stimulation(1, 1)
			-- discards it
			box:remove_stimulation(1, 1)
			
			box:log("Info", string.format("Received new target %s at %ss", identifier, date))	
			
			target = identifier
			targetTime = date
		end		
		
		-- we have a new prediction
		for stimulation = 1, box:get_stimulation_count(2) do			
			-- gets the received stimulation
			identifier, date, duration = box:get_stimulation(2, 1)
			-- discards it
			box:remove_stimulation(2, 1)
	
			-- box:log("Info", string.format("Received stimu %s at %ss", identifier, date))
			
			-- keep tally
			if(lista[identifier] == nil) then
				lista[identifier] = 1
			else
				lista[identifier] = lista[identifier] + 1
			end

		end				
		
		box:sleep()
	end


	
end
