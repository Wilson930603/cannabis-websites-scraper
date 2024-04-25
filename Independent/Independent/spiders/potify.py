# -*- coding: utf-8 -*-
import copy
import json
import math

import scrapy

from Independent.spiders.base_spider import BaseSpider


class PotifySpider(BaseSpider):
    name = 'potify'
    allowed_domains = ['potify.net']
    start_urls = [
        'https://potify.net/promo/eastwood-cannabis-calgary',
        # 'https://potify.net/promo/basa-san-francisco-1',
    ]
    query_products_list = {
        "operationName": "GetOfficeProducts",
        "query": "query GetOfficeProducts($slug: String, $offset: Int, $limit: Int, $filter: ProductsFilter) {\n  getProducts(limit: $limit, offset: $offset, filter: $filter, officeSlug: $slug) {\n    count\n    list {\n      ...ProductFromList\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ProductFromList on Product {\n  id\n  name\n  strain\n  slug\n  url\n  symbol\n  label\n  prices {\n    id\n    isSpecial\n    price\n    rangeFrom\n    rangeTo\n    specialPrice\n    type\n    promoCode {\n      name\n      value\n      __typename\n    }\n    __typename\n  }\n  small_cover {\n    strain_small_cover_list\n    strain_small_cover_list_2x\n    __typename\n  }\n  logo {\n    x1\n    x2\n    __typename\n  }\n  logoList {\n    x1\n    x2\n    __typename\n  }\n  labResult {\n    thc\n    cbd\n    cbn\n    measurement\n    __typename\n  }\n  category {\n    id\n    name\n    __typename\n  }\n  officeSlug\n  brandProduct {\n    id\n    brand {\n      id\n      name\n      logo {\n        x1\n        x2\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n",
        "variables": {
            "filter": {},
            "limit": 40,
            "offset": 0,
            "slug": ''
        }
    }
    query_product_details = {
        "operationName": "Product",
        "query": "query Product($officeSlug: String!, $slug: String!) {\n  product(officeSlug: $officeSlug, slug: $slug) {\n    id\n    slug\n    url\n    name\n    symbol\n    strain\n    label\n    category {\n      name\n      id\n      __typename\n    }\n    prices {\n      id\n      isSpecial\n      price\n      quantity\n      rangeFrom\n      rangeTo\n      specialPrice\n      type\n      promoCode {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    labResult {\n      thc\n      cbd\n      cbn\n      measurement\n      __typename\n    }\n    small_cover {\n      strain_small_cover_list\n      strain_small_cover_list_2x\n      __typename\n    }\n    cover {\n      product_cover_profile_2x\n      product_cover_profile\n      __typename\n    }\n    logo {\n      x1\n      x2\n      __typename\n    }\n    logoList {\n      x1\n      x2\n      __typename\n    }\n    description\n    category {\n      id\n      name\n      __typename\n    }\n    officeSlug\n    brandProduct {\n      id\n      slug\n      name\n      logo {\n        x1\n        x2\n        __typename\n      }\n      strain {\n        id\n        name\n        slug\n        url\n        logoList {\n          x1\n          x2\n          __typename\n        }\n        __typename\n      }\n      strainType\n      description\n      aggregateRating\n      reviewCount\n      photoCount\n      photos {\n        id\n        url\n        __typename\n      }\n      brand {\n        id\n        slug\n        name\n        logo {\n          x1\n          x2\n          __typename\n        }\n        aggregateRating\n        reviewCount\n        __typename\n      }\n      hasEffects\n      effects\n      flavors\n      medicalUses\n      moodsActivities\n      symptoms\n      reviews {\n        id\n        aggregateRating\n        reviewBody\n        dateCreated\n        authorName\n        authorAvatar\n        isVerified\n        likeCount\n        dislikeCount\n        likedByUser\n        dislikedByUser\n        productId\n        productSlug\n        productName\n        effects {\n          positiveEffects\n          medicalEffects\n          negativeEffects\n          condition\n          flavours\n          __typename\n        }\n        photos\n        __typename\n      }\n      __typename\n    }\n    globalProduct {\n      id\n      name\n      slug\n      averageRating\n      reviewsCount\n      photosCount\n      productEffects {\n        effectName\n        value\n        __typename\n      }\n      productFlavors {\n        flavorName\n        __typename\n      }\n      growingNotes\n      growEnvironment\n      height\n      preferredMedium\n      parentGlobalProducts {\n        id\n        name\n        productSlug\n        url\n        label\n        available\n        symbol\n        __typename\n      }\n      photos: photosShort {\n        id\n        photo_thumbnail\n        __typename\n      }\n      reviews: reviewsShort(limit: 3, offset: 0) {\n        id\n        patient {\n          id\n          nickname\n          avatarBackground\n          avatarImage\n          __typename\n        }\n        createdAt\n        isEdited\n        editedAt\n        review\n        rating\n        overallRating\n        parentType\n        photos {\n          id\n          photo_thumbnail\n          __typename\n        }\n        effectsPositive {\n          name\n          __typename\n        }\n        effectsNegative {\n          name\n          __typename\n        }\n        symptoms {\n          name\n          __typename\n        }\n        conditions {\n          name\n          __typename\n        }\n        flavors {\n          name\n          __typename\n        }\n        voteNo\n        voteYes\n        yourVote\n        canReport\n        __typename\n      }\n      __typename\n    }\n    ...Helmet\n    __typename\n  }\n}\n\nfragment Helmet on Product {\n  name\n  description\n  url\n  sharingLogo\n  cover {\n    product_cover_profile\n    __typename\n  }\n  __typename\n}\n",
        "variables": {
            "officeSlug": "420-premium-market-calgary",
            "slug": "24k-goldwoods-3"
        }
    }
    headers = {'Accept': '*/*',
               'Content-Type': 'application/json'}
    sku_types = {1: "1g",
                 2: "1/8 oz (3.5g)",
                 3: "1/4 oz (7g)",
                 4: "1/2 oz (14g)",
                 5: "1 oz (28g)",
                 6: "pre-roll",
                 7: "1 pc"}

    def start_requests(self):
        for url in self.start_urls:
            office_slug = url.split('/')[-1]
            data = {
                "operationName": "GetOfficeWithFullOtherLocation",
                "query": "query GetOfficeWithFullOtherLocation($slug: String, $reviewsLimit: Int, $single: Boolean) {  office(slug: $slug, single: $single) {    id    name    storeName    aboutUs    firstTimeCustomers    announcements    slug    type    promoUrl    site    medibookCompany {      id      __typename    }    hasPickup    hasDelivery    allowMailDelivery    allowOrderOutsideOfBusinessHours    allowScheduledDelivery    usageMedical    usageRecreational    medicalStateLicenseNumber    adultUseStateLicenseNumber    averageRating    reviewsCount    photosCount    dealsCount    presets {      id      name      color      params {        category        __typename      }      image      __typename    }    showCollections    address    fullAddressText    addressText    cityStateZipText    phone    fullPhone    lat    lon    lng    timezone    expressDelivery    delivery {      zones {        lat        lng        __typename      }      subItems {        id        minAmount        hasMinAmount        freeOverOrderCost        feeAmount        hasFeeAmount        processingOrderFrom        processingOrderTo        restrictEndTime        isActive        zones {          lat          lng          __typename        }        __typename      }      hasMinAmount      minAmountMin      minAmountMax      hasFeeAmount      feeAmountMin      feeAmountMax      hasFreeOverOrderCost      freeOverOrderCostMin      freeOverOrderCostMax      __typename    }    pickup {      minOrderCost      __typename    }    canReview    cashback    signup    favorite {      id      createdAt      type      __typename    }    sharingLogo    youtubeVideoId    cover {      office_cover_profile      office_cover_profile_2x      office_cover_list      office_cover_list_2x      __typename    }    promoCovers    logo {      office_logo_profile      office_logo_profile_2x      office_logo_list      office_logo_list_2x      __typename    }    schedules {      openTime      closeTime      dayNumber      __typename    }    shippingInfo    currentUtcTime    otherLocations {      id      slug      type      name      url      promoUrl      fullAddressText      addressText      cityStateZipText      averageRating      reviewsCount      lat      lon      lng      timezone      phone      hasDelivery      hasPickup      usageMedical      usageRecreational      logo {        office_logo_profile        office_logo_profile_2x        office_logo_list        office_logo_list_2x        __typename      }      returnCashback      offersSpecialPrices      securityGuard      lounge      acceptsCreditCards      acceptsDebitCards      atm      labTested      eighteenPlus      twentyOnePlus      allDayVerification      mutlipleLocations      offersPhysicalCards      veteransDiscount      walkIns      walletSizedAuthorizations      wheelchairAccessible      disabilityDiscount      workingStatus      todaySchedule      cashback      schedules {        openTime        closeTime        dayNumber        __typename      }      shippingInfo      currentUtcTime      priceRenewalRegular      priceRenewalCultivation      priceNewRegular      priceNewCultivation      expressDelivery      delivery {        zones {          lat          lng          __typename        }        subItems {          id          minAmount          hasMinAmount          freeOverOrderCost          feeAmount          hasFeeAmount          processingOrderFrom          processingOrderTo          restrictEndTime          isActive          zones {            lat            lng            __typename          }          __typename        }        hasMinAmount        minAmountMin        minAmountMax        hasFeeAmount        feeAmountMin        feeAmountMax        __typename      }      acceptOrders      hasPickup      hasDelivery      allowMailDelivery      allowOrderOutsideOfBusinessHours      allowScheduledDelivery      medibookCompany {        id        __typename      }      features {        allowMailOnly        deliveryShift        __typename      }      __typename    }    country {      name      __typename    }    city {      name      __typename    }    state {      shortName      __typename    }    zip    returnCashback    offersSpecialPrices    securityGuard    lounge    acceptsCreditCards    acceptsDebitCards    atm    labTested    eighteenPlus    twentyOnePlus    allDayVerification    mutlipleLocations    offersPhysicalCards    veteransDiscount    walkIns    walletSizedAuthorizations    wheelchairAccessible    disabilityDiscount    workingStatus    todaySchedule    reviews(limit: $reviewsLimit, offset: 0) {      id      patient {        id        nickname        avatarBackground        avatarImage        __typename      }      createdAt      isEdited      editedAt      review      rating      parentType      overallRating      budQualityRating      atmosphereRating      recommendedRating      knowledgeRating      waitTimeRating      staffRating      patientExperienceRating      deliveryTimeRating      parent {        type        __typename      }      voteNo      voteYes      yourVote      canReport      __typename    }    photos(limit: 99, offset: 0) {      id      photo_thumbnail      __typename    }    deals(limit: 8, offset: 0) {      id      name      medibookOffice: office {        id        name        slug        currentUtcTime        __typename      }      discountType      discount      description      endedAt      duration      url: officePromoUrl      __typename    }    languages {      name      __typename    }    acceptOrders    priceRenewalRegular    priceRenewalCultivation    priceNewRegular    priceNewCultivation    promoTheme    promoMenu {      name      url      __typename    }    features {      allowMailOnly      deliveryPriority      hideDeliveryZones      deliveryShift      __typename    }    ...OfficeHelmet    ...OfficeSellVerificationWizard    __typename  }}fragment OfficeHelmet on Office {  name  fullAddressText  country {    name    __typename  }  city {    name    __typename  }  state {    shortName    __typename  }  zip  url  type  logo {    office_logo_profile    office_logo_profile_2x    __typename  }  sharingLogo  seoTitle  seoDescription  __typename}fragment OfficeSellVerificationWizard on Office {  id  name  slug  signup  country {    code    __typename  }  usageMedical  usageRecreational  __typename}",
                "variables": {
                    "single": True,
                    "slug": office_slug
                }
            }
            headers = copy.copy(self.headers)
            headers['Referer'] = url
            yield scrapy.Request('https://potify.net/graphql',
                                 method='POST',
                                 headers=headers,
                                 body=json.dumps(data),
                                 callback=self.parse_store,
                                 meta={'office_slug': office_slug})

    def parse_store(self, response):
        result = json.loads(response.text)
        store = result['data']['office']
        url = f'https://potify.net/promo{store["url"]}'

        item = {"Producer ID": '',
                "p_id": store['id'],
                "Producer": f'{store["name"]} - {store["city"]["name"]}',
                "Description": '',
                "Link": url,
                "SKU": "",
                "City": store["city"]["name"],
                "Province": store["state"]["shortName"],
                "Store Name": store["name"],
                "Postal Code": store.get('zip'),
                "long": store.get('lon'),
                "lat": store.get('lat'),
                "ccc": "",
                "Page Url": "",
                "Active": "",
                "Main image": store.get('sharingLogo'),
                "Image 2": '',
                "Image 3": '',
                "Image 4": '',
                "Image 5": '',
                "Type": "",
                "License Type": "",
                "Date Licensed": "",
                "Phone": store.get('phone'),
                "Phone 2": "",
                "Contact Name": "",
                "EmailPrivate": "",
                "Email": '',
                "Social": "",
                "FullAddress": store.get('fullAddressText'),
                "Address": store.get('address'),
                "Additional Info": "",
                "Created": "",
                "Comment": "",
                "Updated": ""}
        yield item

        headers = copy.copy(self.headers)
        headers['Referer'] = url
        office_slug = response.meta['office_slug']
        data = copy.copy(self.query_products_list)
        data['variables']['slug'] = office_slug
        yield scrapy.Request('https://potify.net/graphql',
                             method='POST',
                             headers=headers,
                             body=json.dumps(data),
                             callback=self.parse,
                             meta={'page': 0,
                                   'office_slug': office_slug,
                                   'p_id': store['id']})

    def parse(self, response, **kwargs):
        office_slug = copy.copy(response.meta['office_slug'])
        pid = copy.copy(response.meta['p_id'])

        result = json.loads(response.text)
        products = result['data']['getProducts']['list']
        for one in products:
            if one['brandProduct']:
                brand = one['brandProduct']['brand']['name']

            url = f'https://potify.net/promo/{office_slug}/product/{one["slug"]}'
            headers = copy.copy(self.headers)
            headers['Referer'] = url
            data = copy.copy(self.query_product_details)
            data['variables']['officeSlug'] = office_slug
            data['variables']['slug'] = one["slug"]
            yield scrapy.Request('https://potify.net/graphql',
                                 method='POST',
                                 headers=headers,
                                 body=json.dumps(data),
                                 callback=self.parse_details,
                                 meta={'office_slug': office_slug,
                                       'p_id': pid})

        if response.meta['page'] == 0:
            headers = copy.copy(self.headers)
            headers['Referer'] = f'https://potify.net/promo/{office_slug}'

            total_pages = math.ceil(result['data']['getProducts']['count'] / 40)
            for page in range(1, total_pages):
                data = copy.copy(self.query_products_list)
                data['variables']['slug'] = office_slug
                data['variables']['offset'] = page * 40
                yield scrapy.Request('https://potify.net/graphql',
                                     method='POST',
                                     headers=headers,
                                     body=json.dumps(data),
                                     callback=self.parse,
                                     meta={'page': page,
                                           'office_slug': office_slug,
                                           'p_id': pid})

    def parse_details(self, response):
        result = json.loads(response.text)
        product = result['data']['product']

        brand = ''
        if product['brandProduct']:
            brand = product['brandProduct']['brand']['name']

        cover_object = product['cover']
        if cover_object:
            image = cover_object['product_cover_profile'].split('?')[0]
        else:
            image = ''

        for variant in product['prices']:
            quantity = variant['quantity']
            old_price = ''
            if variant['specialPrice'] != '0.00':
                price = variant['specialPrice']
                old_price = variant['price']
            else:
                price = variant['price']

            item = {"Page URL": f'https://potify.net/promo/{response.meta["office_slug"]}/product/{product["slug"]}',
                    "Brand": brand,
                    "Name": product['name'],
                    "SKU": self.sku_types[variant['type']],
                    "Out stock status": 'IN STOCK' if quantity > 0 else 'OUT OF STOCK',
                    "Stock count": quantity,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": price,
                    "Manufacturer": '',
                    "Main image": image,
                    "Description": product.get('description'),
                    "Product ID": product.get('id'),
                    "Additional Information": '',
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": old_price,
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": '',
                    "Option": "amount",
                    "Option type": 'Select',
                    "Option Value": self.sku_types[variant['type']],
                    "Option image": "",
                    "Option price prefix": price,
                    "Cat tree 1 parent": product.get('category').get('name'),
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": "",
                    "Cat tree 2 level 1": "",
                    "Cat tree 2 level 2": "",
                    "Cat tree 2 level 3": "",
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Sort order": "",
                    "Attribute 1": "CBD",
                    "Attribute Value 1": product.get('labResult').get('cbd'),
                    "Attribute 2": "THC",
                    "Attribute value 2": product.get('labResult').get('thc'),
                    "Attribute 3": "CBN",
                    "Attribute value 3": product.get('labResult').get('cbn'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant['id'],
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": response.meta['p_id']}
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('potify')
    process.start()
