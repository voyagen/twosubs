local mp = require 'mp'
local options = require 'mp.options'

-- ponytail: fixed spacing can overlap tall cues; adjust secondary_pos, measure cue bounds if needed.
local opts = { primary_pos = 100, secondary_pos = 82 }
options.read_options(opts, 'twosubs')

local function position(name, value, fallback)
    if value ~= value or value < 0 or value > 100 then
        mp.msg.warn(name .. ' must be between 0 and 100; using ' .. fallback)
        return fallback
    end
    return value
end

opts.primary_pos = position('primary_pos', opts.primary_pos, 100)
opts.secondary_pos = position('secondary_pos', opts.secondary_pos, 82)

mp.set_property_number('sub-pos', opts.primary_pos)
mp.set_property('sub-align-y', 'bottom')
mp.set_property_number('secondary-sub-pos', opts.secondary_pos)
-- Strip authored placement so dialogue stays at the bottom, including ASS.
mp.set_property('sub-ass-override', 'strip')
mp.set_property('secondary-sub-ass-override', 'strip')

local function swap()
    local primary = mp.get_property_native('sid', 'no')
    local secondary = mp.get_property_native('secondary-sid', 'no')
    -- A track cannot occupy both slots: release both before swapping.
    mp.set_property('sid', 'no')
    mp.set_property('secondary-sid', 'no')
    mp.set_property_native('sid', secondary)
    mp.set_property_native('secondary-sid', primary)
    mp.osd_message('Subtitle tracks swapped')
end

mp.add_key_binding('k', 'secondary-next', function()
    mp.command('cycle secondary-sid')
end)
mp.add_key_binding('K', 'secondary-prev', function()
    mp.command('cycle secondary-sid down')
end)
mp.add_key_binding('u', 'swap', swap)
mp.add_key_binding('Ctrl+r', 'secondary-down', function()
    local pos = mp.get_property_number('secondary-sub-pos', opts.secondary_pos)
    mp.set_property_number('secondary-sub-pos', math.min(100, pos + 1))
end, { repeatable = true })
mp.add_key_binding('Ctrl+R', 'secondary-up', function()
    local pos = mp.get_property_number('secondary-sub-pos', opts.secondary_pos)
    mp.set_property_number('secondary-sub-pos', math.max(0, pos - 1))
end, { repeatable = true })
