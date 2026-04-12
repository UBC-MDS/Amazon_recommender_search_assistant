# Step 4: Qualitative Evaluation

**Data source:** `data/processed/appliances_clean.parquet` — **10** documents after loading.

## 4.1 Query Set

| Difficulty | Query |
|---|---|
| Easy | wireless bluetooth headphones |
| Easy | stainless steel water bottle 1 liter |
| Easy | kids lego star wars set |
| Medium | headphones that block airplane noise |
| Medium | something to keep water cold all day |
| Medium | toy for a child who likes space battles |
| Complex | best headphones for long flights under 200 dollars |
| Complex | what is a good educational toy for a 7-year-old interested in space |
| Complex | useful kitchen appliance for quick healthy meals in a small apartment |
| Complex | portable speaker for outdoor use with long battery life |

## 4.2 Retrieve Results

### wireless bluetooth headphones

**Difficulty:** Easy

**BM25 Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 5.5980
2. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 2.0479

**Semantic Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.3880
2. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.1220

### stainless steel water bottle 1 liter

**Difficulty:** Easy

**BM25 Top 5**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 12.1299
2. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 1.5228

**Semantic Top 5**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.5365
2. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.0638

### kids lego star wars set

**Difficulty:** Easy

**BM25 Top 5**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 6.0386

**Semantic Top 5**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.2124

### headphones that block airplane noise

**Difficulty:** Medium

**BM25 Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 6.0766

**Semantic Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.3237

### something to keep water cold all day

**Difficulty:** Medium

**BM25 Top 5**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 7.4703
2. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 2.8947
3. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 1.5228
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 1.4968
5. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 1.4473

**Semantic Top 5**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.3176
2. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.0915
3. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.0575
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 0.0543
5. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 0.0497

### toy for a child who likes space battles

**Difficulty:** Medium

**BM25 Top 5**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 7.5602
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 1.4716
3. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 1.4277
4. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 1.1139
5. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.9683

**Semantic Top 5**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.2951
2. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.0751
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.0542
4. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0438
5. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.0365

### best headphones for long flights under 200 dollars

**Difficulty:** Complex

**BM25 Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 5.8368
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 2.9433
3. **Budget Dishwasher Cleaner Tablets**  
   - Review: Keeps the dishwasher fresh and works well for regular maintenance.  
   - Rating: ★★★★☆ (4.0)  
   - Score: 0.2306
4. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.2136
5. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.2110

**Semantic Top 5**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.2030
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0832
3. **Budget Dishwasher Cleaner Tablets**  
   - Review: Keeps the dishwasher fresh and works well for regular maintenance.  
   - Rating: ★★★★☆ (4.0)  
   - Score: 0.0250
4. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.0232
5. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.0221

### what is a good educational toy for a 7-year-old interested in space

**Difficulty:** Complex

**BM25 Top 5**

1. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 16.7606
2. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 7.9471
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 3.5137
4. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 1.8002
5. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 1.4716

**Semantic Top 5**

1. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.4743
2. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.2433
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.1089
4. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.0503
5. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0349

### useful kitchen appliance for quick healthy meals in a small apartment

**Difficulty:** Complex

**BM25 Top 5**

1. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 16.8199
2. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 2.8287
3. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 2.0895
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 1.7078
5. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 1.0511

**Semantic Top 5**

1. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.5976
2. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.1134
3. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 0.0707
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 0.0696
5. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.0351

### portable speaker for outdoor use with long battery life

**Difficulty:** Complex

**BM25 Top 5**

1. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 10.9698
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 2.4571
3. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 2.2676
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 1.7078
5. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 1.5154

**Semantic Top 5**

1. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.4804
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0911
3. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 0.0777
4. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.0773
5. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.0679

## 4.3 Compare Results

### headphones that block airplane noise

**BM25**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 6.0766

**Semantic Search**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.3237

**Comments**

- **Agreement:** Both methods rank the same item first (**Noise Cancelling Wireless Headphones**). BM25 score 6.0766 vs semantic 0.3237.
- **Top-5 overlap:** 1 distinct document(s) appear in both ranked lists (low agreement).

### something to keep water cold all day

**BM25**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 7.4703
2. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 2.8947
3. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 1.5228
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 1.4968
5. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 1.4473

**Semantic Search**

1. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.3176
2. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.0915
3. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.0575
4. **Smart Blender for Smoothies**  
   - Review: Blends frozen fruit smoothly and the preset modes are easy to use every morning.  
   - Rating: ★★★★☆ (4.4)  
   - Score: 0.0543
5. **Desk Lamp with Adjustable Brightness**  
   - Review: Useful for reading and working at night because the light levels are easy to adjust.  
   - Rating: ★★★★☆ (4.1)  
   - Score: 0.0497

**Comments**

- **Agreement:** Both methods rank the same item first (**Insulated Stainless Steel Water Bottle 1 Liter**). BM25 score 7.4703 vs semantic 0.3176.
- **Top-5 overlap:** 5 distinct document(s) appear in both ranked lists (high agreement).

### toy for a child who likes space battles

**BM25**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 7.5602
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 1.4716
3. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 1.4277
4. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 1.1139
5. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.9683

**Semantic Search**

1. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.2951
2. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.0751
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.0542
4. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0438
5. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.0365

**Comments**

- **Agreement:** Both methods rank the same item first (**Star Space Battle Building Set**). BM25 score 7.5602 vs semantic 0.2951.
- **Top-5 overlap:** 5 distinct document(s) appear in both ranked lists (high agreement).

### best headphones for long flights under 200 dollars

**BM25**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 5.8368
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 2.9433
3. **Budget Dishwasher Cleaner Tablets**  
   - Review: Keeps the dishwasher fresh and works well for regular maintenance.  
   - Rating: ★★★★☆ (4.0)  
   - Score: 0.2306
4. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.2136
5. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.2110

**Semantic Search**

1. **Noise Cancelling Wireless Headphones**  
   - Review: Blocks engine noise on long flights and has comfortable ear pads for all-day listening.  
   - Rating: ★★★★★ (4.7)  
   - Score: 0.2030
2. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0832
3. **Budget Dishwasher Cleaner Tablets**  
   - Review: Keeps the dishwasher fresh and works well for regular maintenance.  
   - Rating: ★★★★☆ (4.0)  
   - Score: 0.0250
4. **Bluetooth Speaker for Outdoor Use**  
   - Review: Loud enough for picnics, water resistant, and the battery lasts through an afternoon outside.  
   - Rating: ★★★★☆ (4.2)  
   - Score: 0.0232
5. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.0221

**Comments**

- **Agreement:** Both methods rank the same item first (**Noise Cancelling Wireless Headphones**). BM25 score 5.8368 vs semantic 0.2030.
- **Top-5 overlap:** 5 distinct document(s) appear in both ranked lists (high agreement).
- **Constraint note:** Our indexed `search_text` does not include numeric **price** fields, so neither method truly optimizes for “under $X”; both approximate via words like “budget” or product copy if present. A reranker or metadata filter would help.

### what is a good educational toy for a 7-year-old interested in space

**BM25**

1. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 16.7606
2. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 7.9471
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 3.5137
4. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 1.8002
5. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 1.4716

**Semantic Search**

1. **Educational Science Kit for Children**  
   - Review: Encourages curiosity with hands-on experiments and is a good gift for a 7-year-old interested in science.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.4743
2. **Star Space Battle Building Set**  
   - Review: A fun educational toy for kids who like space ships, missions, and creative building.  
   - Rating: ★★★★★ (4.6)  
   - Score: 0.2433
3. **Compact Air Fryer Oven**  
   - Review: Great for quick healthy meals and fits well in a small apartment kitchen.  
   - Rating: ★★★★☆ (4.5)  
   - Score: 0.1089
4. **Insulated Stainless Steel Water Bottle 1 Liter**  
   - Review: Keeps water cold all day during hikes and fits easily into a backpack side pocket.  
   - Rating: ★★★★★ (4.8)  
   - Score: 0.0503
5. **Travel Neck Pillow with Memory Foam**  
   - Review: Makes long flights more comfortable and supports the neck without taking much luggage space.  
   - Rating: ★★★★☆ (4.3)  
   - Score: 0.0349

**Comments**

- **Agreement:** Both methods rank the same item first (**Educational Science Kit for Children**). BM25 score 16.7606 vs semantic 0.4743.
- **Top-5 overlap:** 5 distinct document(s) appear in both ranked lists (high agreement).

## 4.4 Summarize Insights

- **BM25:** Best when the user query contains tokens that literally appear in titles or reviews (easy keyword queries). It can over-promote incidental keyword overlap (e.g., shared words across unrelated appliances).
- **Semantic search:** Best when the query is phrased by intent (“block airplane noise”) rather than product names. It can still return plausible-but-wrong items when many products share broad semantics in a small corpus.
- **Where BM25 tends to fail:** Synonyms and paraphrases that do not share stems with the document text; semantic search often recovers these.
- **Where semantic tends to fail:** Very specific SKU-like strings, rare brand tokens, or when every document looks moderately similar in embedding space; BM25 can be sharper.
- **Hard for both:** Multi-constraint questions (price + audience + scenario) without explicit features in the indexed text; hybrid fusion, metadata filters, or a reranker are natural next steps.
