###############################################################################
# (c) 2005-2015 Copyright, Real-Time Innovations.  All rights reserved.       #
# No duplications, whole or partial, manual or electronic, may be made        #
# without express written permission.  Any such copies, or revisions thereof, #
# must display this notice unaltered.                                         #
# This code contains trade secrets of Real-Time Innovations, Inc.             #
###############################################################################

from time import sleep

# Updating the system path is not required if you have pip-installed
# rticonnextdds-connector
from sys import path as sys_path
from os import path as os_path
file_path = os_path.dirname(os_path.realpath(__file__))
sys_path.append(file_path + "/../../../")

import rticonnextdds_connector as rti

with rti.open_connector(
        config_name="DomainParticipantLibraryRR::ParticipantRequester",
        url=file_path + "/RequestReplyQoS.xml") as connector:

    # A initial sample is sent to get a Writer GUID generated by DDS.
    # If we use a hard-coded writer GUID, samples could be discarded
    # as a sample with the same writer GUID and sequence number may have been
    # received before.
    # This can happen if we restart the requester or we have several executions from the same code.
    output = connector.get_output("RequesterPublisher::GUIDGetterWriter")
    input = connector.get_input ("RequesterSubscriber::GUIDGetterReader")
    writer_guid = [0]*16

    output.write()
    input.wait()
    input.take()
    for sample in input.samples.valid_data_iter:
        writer_guid=sample.info["identity"]["writer_guid"]

    output = connector.get_output("RequesterPublisher::RequesterWriter")
    input = connector.get_input ("RequesterSubscriber::RequesterReader")

    print("Waiting for subscriptions...")
    output.wait_for_subscriptions()

    print("Writing...")
    for i in range(1, 5000):
        request_id = {"writer_guid": writer_guid, "sequence_number": i}
        output.instance['request_member']=i
        output.write(identity=request_id)
        print("Request sent")
        reply_received=False
    # We use a while loop as this requester may receive samples from other requester,
    # We make sure we get the reply before sending more request.
    # Other way we couldn't correlate samples because of the sequence number     
        while (not reply_received):
            input.wait()
            input.take()

            for sample in input.samples.valid_data_iter:
                if (sample.info['related_sample_identity']==request_id):
                    print("Reply received")
                    reply_received=True

        sleep(0.5) # Write at a rate of one sample every 0.5 seconds, for ex.

    print("Exiting...")
    output.wait() # Wait for all subscriptions to receive the data before exiting