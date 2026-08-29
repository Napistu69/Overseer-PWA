---
title: "Data Collection Vectors"
weight: 6
description: "By 2012, Flurry Analytics alone was embedded in approximately one million applications, collecting data from two billion smartphones worldwide. The surveillance was happening at the SDK level."
---


## PREAMBLE: THE INFRASTRUCTURE Hiding INSIDE THE INFRASTRUCTURE

The App Store launched in July 2008 with 500 applications. By 2012, Flurry Analytics alone, just one of many analytics SDKs operating silently inside apps, was embedded in approximately one million applications and collecting data from roughly two billion smartphones worldwide. That is staggering scale for a single tracking provider. And Flurry was not unique. It was representative of an entire ecosystem.

To understand what happened, you have to understand what a Software Development Kit actually is. When a developer builds an app, they rarely write every component from scratch. They import pre-packaged code libraries called SDKs that handle specific functions: displaying advertisements, tracking crashes, measuring user engagement, processing payments, integrating social login. These SDKs are written by third-party companies and embedded directly into the app's code. The user downloads the app from the App Store or Google Play. They see the app's interface and functionality. They never see the SDKs running underneath.

Each SDK operates as a silent data collection module. When you open an app, the analytics SDK records that you opened it. When you tap a button, it records the tap. When you scroll, it records the scroll depth. When you pause on a screen, it records the dwell time. When you close the app, it records the session duration. All of this data is transmitted to the SDK provider's servers, not the app developer's servers. The app developer may only see aggregated summary statistics. The SDK provider sees the raw behavioral data.

## THE UDID AND IDENTIFIER ECOSYSTEM

Between 2008 and 2012, the primary device identifier enabling this tracking was the UDID, the Unique Device Identifier. This was a permanent hardware-level identifier burned into every iPhone. Any SDK embedded in any app on that device could read the UDID and use it to correlate activity across every app containing that SDK. If you used a flashlight app, a weather app, a social media app, and a game, and all four contained the same advertising SDK, that SDK provider could stitch together your activity across all four applications into a unified behavioral profile. You never consented to this. You never knew it was happening. The UDID never changed. There was no way to reset it.

This is the critical point. The surveillance was not happening at the app level. It was happening at the SDK level, invisible to both users and regulators. A user might carefully choose which apps to install, believing they were exercising discretion. But the SDK layer operated beneath their awareness, crossing all app boundaries, compiling unified behavioral records regardless of which apps the user selected.

The Path scandal forced Apple to introduce explicit permission prompts for address book access in iOS 5.1 and eventually to deprecate the UDID entirely. The UDID was first discouraged in iOS 5, restricted in iOS 6, and fully removed for third-party use by iOS 7. It was replaced by the IDFA, the Identifier for Advertisers, and the IDFV, the Identifier for Vendor. The IDFA could be reset by the user. The IDFV was unique per app vendor rather than per device.

But here is what the reform actually accomplished. It did not stop data collection. It changed the identifier. The SDK ecosystem adapted. Instead of relying solely on a permanent hardware identifier, SDKs began employing device fingerprinting techniques that combined dozens of data points including device model, operating system version, screen resolution, installed fonts, timezone settings, language preferences, and battery level to create a unique device signature. This fingerprint could identify a device with high probability even without a persistent identifier, and it could not be reset by the user because it was based on legitimate system properties.

---

## THE CONTACTS SCANDAL

In early 2012, a developer named Dustin Curtiss discovered that the social networking app Path was silently uploading users' entire address books to its servers and storing them permanently. Not just the user's own contacts, but every name, phone number, email address, mailing address, birthday, and note stored in the device's contact database. No permission prompt. No notification. No consent.

The Path scandal was the tip of the iceberg. Investigation revealed that Path was not alone. Numerous apps across both iOS and Android were accessing and uploading address book data without permission. The practice was widespread. Apple's own App Store guidelines technically prohibited it, but enforcement was nonexistent. Apps were uploading contact databases and the data was being stored, analyzed, and in many cases sold or shared.

The FTC launched an investigation. Path settled with the FTC in 2013, admitting it had collected personal information from mobile address books without consent. But the settlement was treated as an isolated case when the practice had been systemic. The address book upload was particularly insidious because it did not just collect the user's data. It collected data about every person in that user's life. If you had 500 contacts and installed an app that uploaded your address book, the app developer now possessed the contact information of 500 people who never downloaded the app, never consented to anything, and had no idea their information had been harvested.

This is viral data collection. Each user who consented unknowingly betrayed the privacy of everyone they knew. The network effects were exponential. One user's address book exposes hundreds of contacts. Those contacts' phone numbers and email addresses can then be cross-referenced with other databases to build comprehensive identity graphs far beyond what any individual user ever agreed to share.

---

## PERMISSION MODEL ABUSE

The permission model changes on Android were equally instructive. Early Android versions granted all declared permissions at install time. When a user installed an app, they saw a list of permissions and either accepted all of them or could not install the app. There was no granular control. A weather app could request access to contacts, microphone, camera, and location simultaneously. If the user wanted the weather app, they had to surrender everything. This is coercive consent. The choice was not meaningful. It was all or nothing.

Android 6.0 in 2015 finally introduced runtime permissions, requiring apps to request sensitive permissions at the time of use rather than installation. But by then, five years of unrestricted data collection had already occurred. Billions of devices had been profiled. The behavioral baselines were established. The damage was done.

Meanwhile, the advertising SDK ecosystem was fusing with the data broker industry. Companies like Flurry, AdMob, Millennial Media, and Mobclix were collecting behavioral data across millions of apps. This data was being aggregated, anonymized in name only, and sold to the same data brokers we identified earlier: Acxiom, Experian, CoreLogic. The mobile behavioral data enriched existing profiles with temporal and locational context that desktop web tracking could never provide. Now they knew not just what you browsed, but where you were when you browsed it, how long you looked at it, whether you were walking or sitting, and what you did immediately before and after.

---

## SYNTHESIS

The 2014 Cambridge Analytica scandal demonstrated the endpoint of this architecture. The Facebook-hosted personality quiz app thisisyourdigitallife accessed not only users' data but their friends' data through Facebook's open API. It harvested friends lists, effectively contacts, and through Facebook's location API, precise whereabouts. This data was passed to Cambridge Analytica for political profiling and microtargeting. A single quiz app installed by approximately 270,000 users ultimately exposed the personal data of up to 87 million Facebook users through the viral network effects of the social graph.

The pattern is consistent across every vector. The app was the frontend. The SDK was the harvesting mechanism. The social graph was the amplifier. The data broker was the aggregator. The advertiser or political operative was the customer. The user was the product.

And underneath all of this, every interaction with every app was being logged by the operating system itself. Both iOS and Android maintained diagnostic and usage logs that tracked app launches, session durations, notification interactions, and system events. These logs were accessible to law enforcement through forensic tools during device seizure. Even if an app developer was ethical and collected no data, the operating system itself was maintaining a behavioral record that could be extracted and analyzed.

By 2013, the mobile data collection infrastructure had surpassed anything the desktop web had achieved. The smartphone was always with you, always on, always connected, always logging. The SDK ecosystem ensured that even apps that appeared benign were feeding data to the surveillance layer beneath. The permission system provided the illusion of control while facilitating comprehensive collection. The viral address book uploads meant even non-users were being profiled.

The behavioral data flowing from two billion smartphones through millions of apps was creating the richest training corpus imaginable for machine learning systems. Every tap, every scroll, every hesitation, every notification response, every location visit, every app switch was being recorded and stored. Not for the user's benefit. For the benefit of systems being built to understand, predict and shape human behavior.

The 20-year training cycle Altman referenced was generating its data in real time, through every smartphone on the planet, and the subjects carrying the devices had no idea they were generating it.

---

*"The app was the frontend. The SDK was the harvesting mechanism. The social graph was the amplifier. The data broker was the aggregator. The advertiser or political operative was the customer. The user was the product."*